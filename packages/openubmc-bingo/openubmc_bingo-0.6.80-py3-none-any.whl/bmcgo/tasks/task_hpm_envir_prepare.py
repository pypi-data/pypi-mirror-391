#!/usr/bin/env python3
# coding:utf-8
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import os
import subprocess
import time
from multiprocessing import Process

from bmcgo.tasks.task import Task
from bmcgo import errors


class TaskClass(Task):
    skip_post_hpm = False

    @staticmethod
    def get_shell_command_result(cmd):
        ret = subprocess.getstatusoutput(cmd)
        if ret[0] == 1:
            raise Exception(f"运行命令 {cmd} 失败")
        return ret[1]

    def set_skip_post_hpm(self, value):
        if value:
            self.skip_post_hpm = True
        else:
            self.skip_post_hpm = False

    def copy_file_or_dir(self, src_dir, dst_dir):
        self.pipe_command(["yes y", f"cp -ai {src_dir} {dst_dir}"])
        return

    def prepare_hpm(self):
        hpm_build_dir = self.config.hpm_build_dir
        hpm_build_dir_src = f"/usr/share/bingo/ipmcimage"
        self.tools.copy_all(hpm_build_dir_src, hpm_build_dir)

        self.run_command(f"cp {self.config.board_path}/update_ext4.cfg {hpm_build_dir}/update.cfg")

        self.chdir(hpm_build_dir)
        if not self.skip_post_hpm:
            self._component_cust_action("post_hpm")

        curr_ver = self.get_shell_command_result("cat update.cfg | grep '^Version=' | awk -F '=' '{print $2}'")

        # 读取发布时用的包名
        vs = self.config.version.split(".")
        if self.manufacture_version_check(f"{self.config.board_path}/manifest.yml") is True:
            vs[3] = str(int(vs[3]) + 1).zfill(2)
        ver = f"{vs[0]}.{vs[1]}.{vs[2]}.{vs[3]}"

        # 正常包
        self.info(f"bmc 版本: {ver}")
        self.run_command(
            f"sed -i \"/^Version=/s/{curr_ver}/{ver}/g\" update.cfg")
        self.run_command("chmod +x . -R")

    def sign_img(self):
        if self.config.self_sign:
            self.self_sign()
        else:
            self.online_sign()

    # 自签名函数，继承类可扩展，不能变更方法名，重要!!!
    def self_sign(self):
        self.signature(
            f"{self.config.work_out}/rootfs_BMC.img",
            f"{self.config.work_out}/rootfs_BMC.img.cms",
            f"{self.config.work_out}/cms.crl",
            f"{self.config.work_out}/rootca.der",
        )

    # 在线签名函数，继承类可扩展，不能变更方法名，重要!!!
    def online_sign(self):
        # bingo无需在线签名逻辑，仅占位满足后续流程即可
        out_file = f"{self.config.work_out}/rootfs_BMC.img.cms"
        self.pipe_command([f"echo 'cms placeholder'"], out_file=out_file)

    def tar_img(self):
        self.run_command("tar --format=gnu --exclude BMC_rootfs.tar.gz -czf rootfs_BMC.tar.gz rootfs_BMC.img")
        self.success("tar BMC_rootfs.tar.gz successfully")

    def run(self):
        # 签名
        self.chdir(self.config.build_path)
        self.sign_img()
        self.prepare_hpm()
        # 压缩
        self.chdir(self.config.work_out)
        self.tar_img()
