#!/usr/bin/env python3
# encoding=utf-8
# 描述：根据conan包拉取组件代码
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import json
import os
import re
import shutil
import subprocess
from multiprocessing import Pool, Manager
import patch_ng
import yaml
from git import Repo, exc

from bmcgo import errors
from bmcgo import misc
from bmcgo.utils.tools import Tools

tools = Tools("fetch_component_code")
log = tools.log


def process_err_cb(err):
    log.error("!!!!!!!!!!!!!!!!!!!!!!!!!!! 拉取代码失败, 错误: %s", err)


class FetchComponentCode:
    def __init__(self, packages, target_dir, conan_remote, include_open_source=True):
        self.conan = shutil.which(misc.CONAN)
        if self.conan is None:
            raise RuntimeError("找不到 conan 工具")
        self.packages = packages
        self.target_dir = target_dir
        self.remote = conan_remote
        self.include_open_source = include_open_source

    @staticmethod
    def resolve_version_range(component_name, version_range):
        cmd = f"conan info '{version_range}' --package-filter={component_name}/*" \
             f" -r {misc.conan_remote()} --only None 2>/dev/null"
        if misc.conan_v2():
            cmd = f"conan graph info --requires='{version_range}' --filter {component_name}"
        
        ret, output = subprocess.getstatusoutput(cmd)
        output = output.strip()
        if ret != 0 or not output:
            return None
        return output.split("\n")[-1]

    @staticmethod
    def patch(patch_file=None):
        patchset = patch_ng.fromfile(patch_file)
        if not patchset:
            raise errors.BmcGoException("Failed to parse patch: %s" % (patch_file))
        if not patchset.apply(strip=0, root="./", fuzz=False):
            raise errors.BmcGoException("Failed to apply patch: %s" % patch_file)

    @staticmethod
    def _get_patch_changed_files(patch_file):
        files = {}
        for line in open(patch_file):
            if not line.startswith("diff --git"):
                continue
            line = line.strip()
            chunk = line.split()
            a_file = chunk[-2][2:]
            b_file = chunk[-1][2:]
            files[a_file] = b_file
        return files

    @staticmethod
    def _apply_patches_direct(real_patch, patch_file, changed_files):
        FetchComponentCode.patch(patch_file=real_patch)
        for a_file, b_file in changed_files.items():
            if a_file != b_file:
                if a_file != "/dev/null" and b_file != "/dev/null":
                    os.rename(a_file, b_file)
                    cmd = f"git rm -f {a_file}"
                    tools.run_command(cmd)
                elif a_file != "/dev/null":
                    cmd = f"git rm -f {a_file}"
                    tools.run_command(cmd)
                    continue
            cmd = f"git add {b_file}"
            tools.run_command(cmd)
        cmd = f"git commit -m \"{patch_file}\""
        tools.run_command(cmd)

    @staticmethod
    def __apply_patches(conandata_file, patches, code_dir):
        cwd = os.getcwd()
        if misc.conan_v1():
            recipe_folder = os.path.join(os.path.dirname(conandata_file), "..", "export_source")
        else:
            recipe_folder = os.path.join(os.path.dirname(conandata_file), "..", "es")
        recipe_folder = os.path.realpath(recipe_folder)
        os.chdir(os.path.join(cwd, code_dir))
        for patch in patches:
            patch_file = patch.get("patch_file")
            if not patch_file:
                log.warning(f"{code_dir} 组件的conandata.yml文件缺少patch_file，跳过git apply操作")
            real_patch = os.path.join(recipe_folder, patch_file)
            if not os.path.isfile(real_patch):
                log.error(f"{code_dir} 组件申明的补丁文件{real_patch}不存在，可能产生错误，请人工处理")
                continue
            changed_files = FetchComponentCode._get_patch_changed_files(real_patch)
            log.info(f"{code_dir} 开始应用源码补丁{patch_file}")
            try:
                FetchComponentCode._apply_patches_direct(real_patch, patch_file, changed_files)
            except errors.BmcGoException as e:
                for a_file, b_file in changed_files.items():
                    cmd = f"git checkout -- {a_file}"
                    tools.run_command(cmd, ignore_error=True)
                    cmd = f"git checkout -- {b_file}"
                    tools.run_command(cmd, ignore_error=True)
                try:
                    cmd = "git am " + real_patch
                    tools.run_command(cmd)
                except Exception as am_e:
                    raise RuntimeError(f"git am 恢复补丁 {patch_file} 失败") from am_e
            log.info(f"{code_dir} 应用源码补丁{patch_file}")
        os.chdir(cwd)

    @staticmethod
    def __update_code_by_commit_id(code_dir, url, commit_id):
        if os.path.exists(code_dir):
            repo = Repo(code_dir)
            repo.git.fetch('origin')
        else:
            Repo.clone_from(url, to_path=code_dir)
            repo = Repo(code_dir)

        repo.index.reset(commit=commit_id, head=True, working_tree=True)
        repo.git.clean('-dfx')
        log.info("更新代码(组件: %s, 地址: %s, 提交节点: %s)", code_dir, url, commit_id)

    @staticmethod
    def __update_code_by_branch(code_dir, deps):
        url = deps['url']
        branch = deps.get("branch", "").split('/')[-1] or deps.get("commit", "")
        if os.path.exists(code_dir):
            repo = Repo(code_dir)
            repo.git.fetch('origin')
        else:
            Repo.clone_from(url, to_path=code_dir)
            repo = Repo(code_dir)
        if re.match(r"^[0-9a-f]{40}$", branch):
            repo.head.reset(branch, working_tree=True)
        elif branch.startswith("refs/tags/"):
            repo.head.reset(branch[len("refs/tags/"):], working_tree=True)
        else:
            repo.git.checkout(branch)
        log.info("更新代码(组件: %s, 地址: %s, 节点: %s)", code_dir, url, branch)

    @staticmethod
    def __update_component_code_by_conandata(name, version, conandata_file):
        with open(conandata_file, 'r') as f_:
            conandata = yaml.safe_load(f_)
            deps = conandata.get("sources", {}).get(version, {})
            if 'url' in deps:
                FetchComponentCode.__update_code_by_branch(name, deps)
                patches = conandata.get("patches", {}).get(version)
                if patches:
                    FetchComponentCode.__apply_patches(conandata_file, patches, name)
            else:
                for comp, deps in deps.items():
                    FetchComponentCode.__update_code_by_branch(comp, deps)

    @staticmethod
    def __getinfo_from_conanfile(conanfile):
        with open(conanfile, "r") as file:
            lines = file.readlines()
            for idx, line in enumerate(lines):
                if line.find('scm = {"revision":') > 0:
                    revision = re.split(r'["]', line)[-2]
                    url = re.split(r'["]', lines[idx + 2])[-2]
                    break
            else:
                raise RuntimeError("无法找到版本(revision)和地址(url)字段")

            return revision, url

    # --- 新增：MDS修补方案 1 (Install) ---
    @staticmethod
    def _try_mds_install_plan(conan_version, component_name):
        """
        尝试使用 'conan install' 来获取 package_folder
        """
        log.info(f"MDS修补 (方案1: install): 正在尝试 {conan_version}...")
        cmd_install = f"conan install --requires={conan_version} -r openubmc_dev\
                      --build=missing -pr profile.ini --format=json --output-folder=tmp"
        
        command_result = tools.run_command(cmd_install, capture_output=True, ignore_error=True)
        stdout = command_result.stdout.strip()
        stderr = command_result.stderr.strip()

        if command_result.returncode != 0 or not stdout:
            log.warning(f"MDS修补 (方案1: install) 失败: 命令执行失败。 STDERR: {stderr}")
            raise RuntimeError(f"Install plan failed (command error). stderr: {stderr}")

        try:
            result = json.loads(stdout)
            nodes = result.get("graph", {}).get("nodes", {})
            package_folder = None
            for node in nodes.values():
                if node.get("ref") and node.get("ref").startswith(conan_version):
                    package_folder = node.get("package_folder")
                    if package_folder:
                        break
            
            if not package_folder:
                log.warning(f"MDS修补 (方案1: install) 失败: 未在JSON中找到 package_folder。")
                raise RuntimeError("Install plan failed (JSON parse).")
            
            log.info(f"MDS修补 (方案1: install) 成功。 找到 package_folder: {package_folder}")
            return package_folder # 成功
        except Exception as json_err:
            log.warning(f"MDS修补 (方案1: install) 失败: JSON解析错误。 {json_err}")
            raise RuntimeError(f"Install plan failed (JSON parse).") from json_err

    # --- 新增：MDS修补方案 2 (Download) ---
    @staticmethod
    def _try_mds_download_plan(conan_version, component_name):
        """
        尝试使用 'conan download' (不带profile) 来获取 package_folder
        """
        log.warning(f"MDS修补 (方案1: install) 失败。 切换到 (方案2: download)...")
        try:
            cmd_download = f"conan download {conan_version} -r openubmc_dev --format=json"
            log.info(f"MDS修补 (方案2: download): 执行: {cmd_download}")
            command_result = tools.run_command(cmd_download, capture_output=True, ignore_error=True)
            stdout = command_result.stdout.strip()
            stderr = command_result.stderr.strip()

            if command_result.returncode != 0 or not stdout:
                log.error(f"MDS修补 (方案2: download) 失败: 命令执行失败。 STDERR: {stderr}")
                raise RuntimeError(f"Download command failed. STDERR: {stderr}")

            result = json.loads(stdout)
            local_cache = result.get("Local Cache")
            component_info = local_cache.get(conan_version)
            revisions = component_info.get("revisions")
            first_revision_id = next(iter(revisions))
            first_revision_data = revisions[first_revision_id]
            packages = first_revision_data.get("packages")
            first_package_id = next(iter(packages))
            full_pref = f"{conan_version}#{first_revision_id}:{first_package_id}"
            
            cmd_cache_path = f"conan cache path {full_pref}"
            log.info(f"MDS修补 (方案2: download): 执行: {cmd_cache_path}")
            path_cmd_info = tools.run_command(cmd_cache_path, capture_output=True, ignore_error=True)
            
            if path_cmd_info.returncode != 0 or not path_cmd_info.stdout:
                log.error(f"MDS修补 (方案2: download) 失败: 'conan cache path' 失败。 STDERR: {path_cmd_info.stderr.strip()}")
                raise RuntimeError(f"'conan cache path' 失败. STDERR: {path_cmd_info.stderr.strip()}")

            package_folder = path_cmd_info.stdout.strip()
            log.info(f"MDS修补 (方案2: download) 成功。 找到 package_folder: {package_folder}")
            return package_folder # 成功

        except Exception as download_e:
            log.error(f"MDS修补 (方案2: download) 失败: {download_e}")
            raise RuntimeError("Download plan failed.") from download_e

    def run(self):
        packages_to_fetch = dict()
        for component_name, package in self.packages.items():
            version_str = re.split("/|@", package)[1]
            if "[" not in version_str:
                if self.include_open_source or re.fullmatch("\d+\.\d+\.\d+", version_str) is not None:
                    packages_to_fetch[component_name] = package
                continue
            resolved_package = self.resolve_version_range(component_name, package)
            if resolved_package is None:
                log.warning("查找不到与 %s 范围匹配的版本", package)
            else:
                packages_to_fetch[component_name] = resolved_package
                log.info("查找到与 %s 范围匹配的版本 %s", package, resolved_package)

        process_count = min(len(packages_to_fetch), os.cpu_count())
        log.info("创建 %u 个进程拉取代码", process_count)

        manager = Manager()
        conan_lock = manager.Lock()
        
        pool = Pool(processes=process_count)
        for component_name, conan_version in packages_to_fetch.items():
            pool.apply_async(func=self.update_component_code, 
                             args=(component_name, conan_version, conan_lock),
                             error_callback=process_err_cb)
        pool.close()
        pool.join()

    def update_component_code(self, component_name, conan_version, conan_lock):
        """
        update component code by conan version
        """
        try:
            os.chdir(self.target_dir)
            log.info("更新 %s 组件代码到 %s 开始", component_name, conan_version)
            if misc.conan_v1():
                version_split = re.split(r'[/, @]', conan_version)
                conan_dir = os.path.join(os.path.expanduser('~'), '.conan/data/', *version_split, 'export')
                conandata = os.path.join(conan_dir, 'conandata.yml')
                
                with conan_lock:
                    if not os.path.exists(conan_dir):
                        conan_remote_list = tools.get_conan_remote_list(self.remote)
                        tools.download_conan_recipes(conan_version, conan_remote_list)
                
                if os.path.exists(conandata):
                    self.__update_component_code_by_conandata(version_split[0], version_split[1], conandata)
                    return

                conanfile = os.path.join(conan_dir, 'conanfile.py')
                if os.path.exists(conanfile):
                    revision, url = self.__getinfo_from_conanfile(conanfile)
                    self.__update_code_by_commit_id(component_name, url, revision)
                    return
                log.error("conandata(%s) 和 conanfile(%s) 都没有找到", conandata, conanfile)
            else:
                path_cmd_info = None
                with conan_lock:
                    conan_remote_list = tools.get_conan_remote_list(self.remote)
                    tools.download_conan_recipes(conan_version, conan_remote_list)
                    path_cmd = f"conan cache path {conan_version}"
                    path_cmd_info = Tools().run_command(path_cmd, capture_output=True)

                version_split = re.split(r'[/, @]', conan_version)
                conan_dir = path_cmd_info.stdout.strip()
                conandata = os.path.join(conan_dir, 'conandata.yml')
                if os.path.exists(conandata):
                    self.__update_component_code_by_conandata(version_split[0], version_split[1], conandata)
                    return

                log.error("conandata(%s) 没有找到", conandata)
            log.info("更新组件 %s 代码到 %s 失败, 无法获取到 conan 信息", component_name,
                     conan_version)
        except exc.GitError as exp:
            log.warning("Git 操作失败 (组件: %s): %s。 尝试MDS修补...", component_name, exp)
            package_folder = None
            
            with conan_lock:
                try:
                    # --- 方案 1: install (优先) ---
                    package_folder = FetchComponentCode._try_mds_install_plan(conan_version, component_name)
                except Exception as install_e:
                    # --- 方案 2: download (后备) ---
                    try:
                        package_folder = FetchComponentCode._try_mds_download_plan(conan_version, component_name)
                    except Exception as download_e:
                        # --- 两个方案都失败了 ---
                        log.error(f"MDS修补: 方案1 和 方案2 均失败 (组件: {component_name})。")
                        raise RuntimeError(f"MDS修补方案 'install' 和 'download' 均失败 (组件: {component_name})") from exp

            # --- 复制步骤 (锁外) ---
            if package_folder:
                mds_src_path = f"{package_folder}/include"
                if os.path.exists(mds_src_path):
                    src = mds_src_path
                    dest = os.path.abspath(f"{component_name}")
                    shutil.copytree(src, dest, dirs_exist_ok=True)
                    log.info(f"将组件 {component_name} 复制到 {dest}.")
                else:
                    log.warning(f"MDS修补: 在 {package_folder} 中未找到 'include/mds'。")
            else:
                # 这种情况不应该发生，因为如果两个方案都失败了，上面会抛出异常
                log.error(f"MDS修补失败 (组件: {component_name}): 未能获取 package_folder。")
                raise exp # 重新抛出原始 GitError
            
            # 清理 'install' 方案(如果成功)创建的 'tmp' 目录
            shutil.rmtree(f"{self.target_dir}/tmp", ignore_errors=True)
            
        except Exception as exp:
            log.error("工作状态错误 (组件: %s): %s", component_name, exp)
            log.error("更新组件 %s 代码到 %s 失败", component_name, conan_version)