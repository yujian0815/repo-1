import arpy
import tarfile


class DpkgPy:
    """
        dpkgpy是一个python库，设计用于在纯python中创建和操作debian包。
        除了其他Python库之外，它没有依赖项。
        （c）2019 Shuga控股公司。版权所有！
    """
    def __init__(self):
        super(DpkgPy, self).__init__()

    def extract(self, input_path, output_path):
        """
            从DEB文件中提取数据。
            ：param input_path：要提取的DEB文件路径的字符串。
            ：param output_path：放置提取的DEB的文件路径字符串。文件夹必须已经存在。
            ：返回：有关提取是否成功或失败的布尔值。
        """
        try:
            root_ar = arpy.Archive(input_path)
            root_ar.read_all_headers()
            try:
                data_bin = root_ar.archived_files[b'data.tar.gz']
                data_tar = tarfile.open(fileobj=data_bin)
                data_tar.extractall(output_path)
            except Exception:
                data_theos_bin = root_ar.archived_files[b'data.tar.lzma']
                data_theos_bin.seekable = lambda: True
                data_theos_tar = tarfile.open(fileobj=data_theos_bin, mode='r:xz')
                data_theos_tar.extractall(output_path)  # This is an actual Python/lzma implementation bug from the looks of it.

            control_bin = root_ar.archived_files[b'control.tar.gz']
            control_tar = tarfile.open(fileobj=control_bin)
            control_tar.extractall(output_path)
            return True
        except Exception:
            return False

    def control_extract(self, input_path, output_path):
        """
            仅从DEB中提取控制文件
            ：param input_path：要提取的DEB文件路径的字符串。
            ：param output_path：放置提取的DEB的文件路径字符串。文件夹必须已经存在。
            ：返回：有关提取是否成功或失败的布尔值。
        """
        try:
            root_ar = arpy.Archive(input_path)
            root_ar.read_all_headers()
            control_bin = root_ar.archived_files[b'control.tar.gz']
            control_tar = tarfile.open(fileobj=control_bin)
            control_tar.extractall(output_path)
            return True
        except Exception:
            return False

    # TODO: Add support for the creation of DEB files without any dependencies, allowing for improved Windows support.
