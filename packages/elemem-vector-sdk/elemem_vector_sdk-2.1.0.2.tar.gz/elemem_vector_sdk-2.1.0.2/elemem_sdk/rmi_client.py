import os
import sys
import grpc
import logging
import json
import requests
import argparse
from typing import List, Dict, Optional, Tuple
from google.protobuf.json_format import MessageToDict

try:
    from . import rmi_pb2
    from . import rmi_pb2_grpc
except ImportError:
    import rmi_pb2
    import rmi_pb2_grpc

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('RMIClient')
logger.setLevel(logging.INFO)


class RMIClient:
    """
    Resource Manager Interface (RMI) 客户端
    支持资源分配、查询、管理等功能
    """
    
    def __init__(self, server_address: str = "localhost:8000", debug: bool = False, use_http: bool = False):
        """
        初始化RMI客户端
        
        Args:
            server_address: 服务器地址，格式为 "host:port"
            debug: 是否启用调试模式
            use_http: 是否使用HTTP接口（对于部分接口）
        """
        self.server_address = server_address
        self.debug = debug
        self.use_http = use_http
        
        if not use_http:
            # gRPC连接配置
            options = [
                ('grpc.max_receive_message_length', 200 * 1024 * 1024),  # 200MB
                ('grpc.max_send_message_length', 200 * 1024 * 1024),     # 200MB
                ('grpc.keepalive_time_ms', 30000),
                ('grpc.keepalive_timeout_ms', 5000),
                ('grpc.keepalive_permit_without_calls', True),
            ]
            
            self.channel = grpc.insecure_channel(server_address, options=options)
            self.stub = rmi_pb2_grpc.ResourceManagerServiceStub(self.channel)
            self.http_stub = rmi_pb2_grpc.RMIServiceStub(self.channel)
            logger.info(f"Connected to gRPC server at {server_address}")
        else:
            # HTTP连接配置
            self.http_base_url = f"http://{server_address}"
            logger.info(f"Using HTTP interface at {self.http_base_url}")
    
    def _log_full_response(self, response, method_name: str):
        """记录完整的响应信息（调试模式）"""
        if self.debug:
            try:
                response_dict = MessageToDict(
                    response,
                    preserving_proto_field_name=True,
                    always_print_fields_with_no_presence=True
                )
                formatted = json.dumps(
                    response_dict,
                    indent=2,
                    ensure_ascii=False,
                    default=lambda x: str(x)
                )
                logger.debug(f"FULL RESPONSE FOR {method_name}:\n{formatted}")
            except Exception as e:
                logger.error(f"Failed to log full response: {str(e)}")
    
    def _check_response_success(self, response, method_name: str):
        """检查响应是否成功"""
        if hasattr(response, 'success') and not response.success:
            message = getattr(response, 'message', 'Unknown error')
            err_msg = f"{method_name} failed: {message}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)
    
    def _http_request(self, endpoint: str, data: Dict = None, method: str = "POST") -> Dict:
        """发送HTTP请求"""
        url = f"{self.http_base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=data, timeout=30)
            else:
                response = requests.post(url, json=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            raise RuntimeError(f"HTTP request to {endpoint} failed: {e}")
    
    # ==================== 资源分配相关接口 ====================
    
    def allocate_columns(self, index_name: str, bytes_per_vec: int, vec_size: int) -> List[Dict]:
        """
        分配列资源
        
        Args:
            index_name: 索引名称
            bytes_per_vec: 每列的字节数
            vec_size: 需要分配的列数
            
        Returns:
            分配结果列表，每个元素包含分配的资源信息
        """
        logger.info(f"Allocating columns: index={index_name}, bytes_per_vec={bytes_per_vec}, vec_size={vec_size}")
        
        if self.use_http:
            # 使用HTTP接口
            data = {
                "index_name": index_name,
                "bytes_per_vec": bytes_per_vec,
                "vec_size": vec_size
            }
            result = self._http_request("allocate_columns", data)
            if not result.get("success", False):
                raise RuntimeError(f"Column allocation failed")
            return result.get("allocations", [])
        else:
            # 使用gRPC接口
            request = rmi_pb2.AllocateColumnsRequest(
                index_name=index_name,
                bytes_per_vec=bytes_per_vec,
                vec_size=vec_size
            )
            
            response = self.stub.AllocateColumns(request)
            self._log_full_response(response, "AllocateColumns")
            self._check_response_success(response, "AllocateColumns")
            
            allocations = []
            for alloc in response.allocations:
                allocations.append({
                    'host': alloc.host,
                    'vpu_idx': alloc.vpu_idx,
                    'group_idx': alloc.group_idx,
                    'chip_idx': alloc.chip_idx,
                    'bank_idx': alloc.bank_idx,
                    'column_range': {
                        'offset': alloc.column_range.offset,
                        'length': alloc.column_range.length
                    },
                    'ddr_range': {
                        'offset': alloc.ddr_range.offset,
                        'length': alloc.ddr_range.length
                    },
                    'type': alloc.type
                })
            
            logger.info(f"Successfully allocated {len(allocations)} column resources")
            return allocations
    
    def allocate_ddr(self, index_name: str, bytes_per_vec: int, vec_size: int) -> List[Dict]:
        """
        分配DDR资源
        
        Args:
            index_name: 索引名称
            bytes_per_vec: 每向量的字节数
            vec_size: 向量数量
            
        Returns:
            分配结果列表
        """
        logger.info(f"Allocating DDR: index={index_name}, bytes_per_vec={bytes_per_vec}, vec_size={vec_size}")
        
        request = rmi_pb2.AllocateDDRRequest(
            index_name=index_name,
            bytes_per_vec=bytes_per_vec,
            vec_size=vec_size
        )
        
        response = self.stub.AllocateDDR(request)
        self._log_full_response(response, "AllocateDDR")
        self._check_response_success(response, "AllocateDDR")
        
        allocations = []
        for alloc in response.allocations:
            allocations.append({
                'host': alloc.host,
                'vpu_idx': alloc.vpu_idx,
                'group_idx': alloc.group_idx,
                'chip_idx': alloc.chip_idx,
                'bank_idx': alloc.bank_idx,
                'column_range': {
                    'offset': alloc.column_range.offset,
                    'length': alloc.column_range.length
                },
                'ddr_range': {
                    'offset': alloc.ddr_range.offset,
                    'length': alloc.ddr_range.length
                },
                'type': alloc.type
            })
        
        logger.info(f"Successfully allocated {len(allocations)} DDR resources")
        return allocations
    
    def allocate_ddr_by_group(self, host: str, vpu_idx: int, group_idx: int, 
                             index_name: str, bytes_per_vec: int, vec_size: int) -> List[Dict]:
        """
        按组分配DDR资源
        
        Args:
            host: 主机地址
            vpu_idx: VPU索引
            group_idx: Group索引
            index_name: 索引名称
            bytes_per_vec: 每向量的字节数
            vec_size: 向量数量
            
        Returns:
            分配结果列表
        """
        logger.info(f"Allocating DDR by group: {host}:{vpu_idx}:{group_idx}, index={index_name}")
        
        request = rmi_pb2.AllocateDDRByGroupRequest(
            host=host,
            vpu_idx=vpu_idx,
            group_idx=group_idx,
            index_name=index_name,
            bytes_per_vec=bytes_per_vec,
            vec_size=vec_size
        )
        
        response = self.stub.AllocateDDRByGroup(request)
        self._log_full_response(response, "AllocateDDRByGroup")
        self._check_response_success(response, "AllocateDDRByGroup")
        
        allocations = []
        for alloc in response.allocations:
            allocations.append({
                'host': alloc.host,
                'vpu_idx': alloc.vpu_idx,
                'group_idx': alloc.group_idx,
                'chip_idx': alloc.chip_idx,
                'bank_idx': alloc.bank_idx,
                'column_range': {
                    'offset': alloc.column_range.offset,
                    'length': alloc.column_range.length
                },
                'ddr_range': {
                    'offset': alloc.ddr_range.offset,
                    'length': alloc.ddr_range.length
                },
                'type': alloc.type
            })
        
        logger.info(f"Successfully allocated {len(allocations)} DDR resources by group")
        return allocations
    
    def release_columns(self, index_name: str) -> bool:
        """
        释放列资源
        
        Args:
            index_name: 索引名称
            
        Returns:
            释放是否成功
        """
        logger.info(f"Releasing columns for index: {index_name}")
        
        request = rmi_pb2.ReleaseColumnsRequest(index_name=index_name)
        response = self.stub.ReleaseColumns(request)
        self._log_full_response(response, "ReleaseColumns")
        self._check_response_success(response, "ReleaseColumns")
        
        logger.info(f"Successfully released columns for index: {index_name}")
        return True
    
    # ==================== 查询相关接口 ====================
    
    def query_status(self, logid: int = 0) -> Dict:
        """
        查询资源状态
        
        Args:
            logid: 日志ID
            
        Returns:
            资源状态信息
        """
        logger.info("Querying resource status")
        
        if self.use_http:
            # 使用HTTP接口
            result = self._http_request("query_status", method="GET")
            return result
        else:
            # 使用gRPC接口
            request = rmi_pb2.QueryStatusRequest(logid=logid)
            response = self.stub.QueryStatus(request)
            self._log_full_response(response, "QueryStatus")
            
            status = {
                'total_allocated_ddr': response.total_allocated_ddr,
                'total_remaining_ddr': response.total_remaining_ddr,
                'total_allocated_columns': response.total_allocated_columns,
                'total_remaining_columns': response.total_remaining_columns,
                'total_allocated_bars': response.total_allocated_bars,
                'total_remaining_bars': response.total_remaining_bars
            }
            
            logger.info("Successfully queried resource status")
            logger.debug(f"Status: {json.dumps(status, indent=2)}")
            return status
    
    def query_all_group_ddr_status(self) -> List[Dict]:
        """
        查询所有Group的DDR状态
        
        Returns:
            Group DDR状态列表
        """
        logger.info("Querying all group DDR status")
        
        request = rmi_pb2.QueryAllGroupDDRStatusRequest()
        response = self.stub.QueryAllGroupDDRStatus(request)
        self._log_full_response(response, "QueryAllGroupDDRStatus")
        
        groups = []
        for group in response.groups:
            groups.append({
                'host': group.host,
                'cardid': group.cardid,
                'card_dna': group.card_dna,
                'vpu_idx': group.vpu_idx,
                'group_idx': group.group_idx,
                'group_total_ddr': group.group_total_ddr,
                'group_used_ddr': group.group_used_ddr,
                'group_free_ddr': group.group_free_ddr
            })
        
        logger.info(f"Found {len(groups)} groups")
        return groups
    
    def query_global_ddr_status(self) -> Dict:
        """
        查询全局DDR状态
        
        Returns:
            全局DDR状态信息
        """
        logger.info("Querying global DDR status")
        
        request = rmi_pb2.QueryGlobalDDRStatusRequest()
        response = self.stub.QueryGlobalDDRStatus(request)
        self._log_full_response(response, "QueryGlobalDDRStatus")
        
        # 处理组状态列表
        group_status_list = []
        for group in response.group_status_list:
            group_status_list.append({
                'host': group.host,
                'cardid': group.cardid,
                'card_dna': group.card_dna,
                'vpu_idx': group.vpu_idx,
                'group_idx': group.group_idx,
                'group_total_ddr': group.group_total_ddr,
                'group_used_ddr': group.group_used_ddr,
                'group_free_ddr': group.group_free_ddr
            })
        
        # 处理卡状态列表
        card_bar_status_list = []
        for card in response.card_bar_status_list:
            card_bar_status_list.append({
                'host': card.host,
                'cardid': card.cardid,
                'free_bar_count': card.free_bar_count
            })
        
        status = {
            'total_ddr': response.total_ddr,
            'used_ddr': response.used_ddr,
            'free_ddr': response.free_ddr,
            'cardnum': response.cardnum,
            'hostnum': response.hostnum,
            'group_status_list': group_status_list,
            'card_bar_status_list': card_bar_status_list
        }
        
        logger.info("Successfully queried global DDR status")
        logger.debug(f"Global status: {json.dumps(status, indent=2, default=str)}")
        return status
    
    def query_index_allocation(self, index_name: str) -> List[Dict]:
        """
        查询索引的资源分配情况
        
        Args:
            index_name: 索引名称
            
        Returns:
            索引分配结果列表
        """
        logger.info(f"Querying index allocation: {index_name}")
        
        if self.use_http:
            # 使用HTTP接口
            params = {"index_name": index_name}
            result = self._http_request("query_index_allocation", params, method="GET")
            return result.get("allocations", [])
        else:
            # 使用gRPC接口
            request = rmi_pb2.QueryIndexAllocationRequest(index_name=index_name)
            response = self.stub.QueryIndexAllocation(request)
            self._log_full_response(response, "QueryIndexAllocation")
            
            allocations = []
            for alloc in response.allocations:
                allocations.append({
                    'index_name': alloc.index_name,
                    'host': alloc.host,
                    'vpu_idx': alloc.vpu_idx,
                    'group_idx': alloc.group_idx,
                    'chip_idx': alloc.chip_idx,
                    'bank_idx': alloc.bank_idx,
                    'column_range': {
                        'offset': alloc.column_range.offset,
                        'length': alloc.column_range.length
                    },
                    'ddr_range': {
                        'offset': alloc.ddr_range.offset,
                        'length': alloc.ddr_range.length
                    },
                    'resource_type': alloc.resource_type
                })
            
            logger.info(f"Found {len(allocations)} allocations for index {index_name}")
            return allocations
    
    def query_all_index_allocation(self) -> List[Dict]:
        """
        查询所有索引的资源分配情况
        
        Returns:
            所有索引分配结果列表
        """
        logger.info("Querying all index allocations")
        
        request = rmi_pb2.QueryAllIndexAllocationRequest()
        response = self.stub.QueryAllIndexAllocation(request)
        self._log_full_response(response, "QueryAllIndexAllocation")
        
        allocations = []
        for alloc in response.allocations:
            allocations.append({
                'index_name': alloc.index_name,
                'host': alloc.host,
                'vpu_idx': alloc.vpu_idx,
                'group_idx': alloc.group_idx,
                # 'chip_idx': alloc.chip_idx,
                # 'bank_idx': alloc.bank_idx,
                # 'column_offset': alloc.column_offset,
                # 'column_length': alloc.column_length,
                'ddr_offset': alloc.ddr_offset,
                'ddr_length': alloc.ddr_length,
                'resource_type': alloc.resource_type
            })
        
        logger.info(f"Found {len(allocations)} total allocations")
        return allocations
    
    # ==================== 管理相关接口 ====================
    
    def add_card(self, host_id: str, cardid: int, card_dna: str) -> bool:
        """
        添加加速卡
        
        Args:
            host_id: 主机ID
            cardid: 卡ID
            card_dna: 卡DNA
            
        Returns:
            添加是否成功
        """
        logger.info(f"Adding card: host={host_id}, cardid={cardid}, dna={card_dna[:20]}...")
        
        request = rmi_pb2.AddCardRequest(
            host_id=host_id,
            cardid=cardid,
            card_dna=card_dna
        )
        
        response = self.stub.AddCard(request)
        self._log_full_response(response, "AddCard")
        self._check_response_success(response, "AddCard")
        
        logger.info(f"Successfully added card: {host_id}:{cardid}")
        return True
    
    def freeze_group(self, host: str, vpu_idx: int, group_idx: int) -> bool:
        """
        冻结Group
        
        Args:
            host: 主机地址
            vpu_idx: VPU索引
            group_idx: Group索引
            
        Returns:
            冻结是否成功
        """
        logger.info(f"Freezing group: {host}:{vpu_idx}:{group_idx}")
        
        request = rmi_pb2.FreezeGroupRequest(
            host=host,
            vpu_idx=vpu_idx,
            group_idx=group_idx
        )
        
        response = self.stub.FreezeGroup(request)
        self._log_full_response(response, "FreezeGroup")
        self._check_response_success(response, "FreezeGroup")
        
        logger.info(f"Successfully frozen group: {host}:{vpu_idx}:{group_idx}")
        return True
    
    def unfreeze_group(self, host: str, vpu_idx: int, group_idx: int) -> bool:
        """
        解冻Group
        
        Args:
            host: 主机地址
            vpu_idx: VPU索引
            group_idx: Group索引
            
        Returns:
            解冻是否成功
        """
        logger.info(f"Unfreezing group: {host}:{vpu_idx}:{group_idx}")
        
        request = rmi_pb2.UnfreezeGroupRequest(
            host=host,
            vpu_idx=vpu_idx,
            group_idx=group_idx
        )
        
        response = self.stub.UnfreezeGroup(request)
        self._log_full_response(response, "UnfreezeGroup")
        self._check_response_success(response, "UnfreezeGroup")
        
        logger.info(f"Successfully unfrozen group: {host}:{vpu_idx}:{group_idx}")
        return True
    
    def reset_resource_manager(self) -> bool:
        """
        重置资源管理器
        
        Returns:
            重置是否成功
        """
        logger.info("Resetting resource manager")
        
        request = rmi_pb2.ResetResourceManagerRequest()
        response = self.stub.ResetResourceManager(request)
        self._log_full_response(response, "ResetResourceManager")
        self._check_response_success(response, "ResetResourceManager")
        
        logger.info("Successfully reset resource manager")
        return True
    
    # ==================== 工具方法 ====================
    
    def close(self):
        """关闭客户端连接"""
        if hasattr(self, 'channel'):
            self.channel.close()
            logger.info("gRPC connection closed")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

def print_table(data: List[Dict], headers: List[str] = None, title: str = ""):
    """以表格形式美观打印数据"""
    if not data:
        print(f"{title}无数据。")
        return
    from tabulate import tabulate
    print(f"\n{title}")
    if headers is None or headers == "keys":
        print(tabulate(data, headers="keys", tablefmt="grid", stralign="center", numalign="center"))
    else:
        print(tabulate(data, headers=headers, tablefmt="grid", stralign="center", numalign="center"))


def main():
    parser = argparse.ArgumentParser(
        description="RMI Resource Manager 命令行工具"
    )
    parser.add_argument("--server", type=str, default="localhost:7000", help="RMI服务地址 host:port")
    parser.add_argument("--debug", action="store_true", help="开启调试日志")
    parser.add_argument("--http", action="store_true", help="使用HTTP接口")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 查询资源状态
    subparsers.add_parser("status", help="查询资源状态")

    # 查询全局DDR状态
    subparsers.add_parser("global_ddr", help="查询全局DDR状态")

    # 查询所有Group DDR状态
    subparsers.add_parser("group_ddr", help="查询所有Group DDR状态")

    # 查询所有索引分配
    subparsers.add_parser("all_index_alloc", help="查询所有索引分配")

    # 查询单索引分配
    parser_index = subparsers.add_parser("index_alloc", help="查询指定索引分配")
    parser_index.add_argument("index_name", type=str, help="索引名称")

    # 添加加速卡
    parser_addcard = subparsers.add_parser("add_card", help="添加加速卡")
    parser_addcard.add_argument("host_id", type=str, help="主机ID")
    parser_addcard.add_argument("cardid", type=int, help="卡ID")
    parser_addcard.add_argument("card_dna", type=str, help="卡DNA")

    # 分配列资源
    parser_alloc = subparsers.add_parser("alloc_columns", help="分配列资源")
    parser_alloc.add_argument("index_name", type=str)
    parser_alloc.add_argument("bytes_per_vec", type=int)
    parser_alloc.add_argument("vec_size", type=int)
    
    # 分配ddr资源
    parser_alloc_ddr = subparsers.add_parser("alloc_ddr_by_group", help="分配DDR资源")
    parser_alloc_ddr.add_argument("host", type=str)
    parser_alloc_ddr.add_argument("card_idx", type=int)
    parser_alloc_ddr.add_argument("group_idx", type=int)
    parser_alloc_ddr.add_argument("index_name", type=str)
    parser_alloc_ddr.add_argument("bytes_per_vec", type=int)
    parser_alloc_ddr.add_argument("vec_size", type=int)

    # 释放资源
    parser_release = subparsers.add_parser("release", help="释放列资源")
    parser_release.add_argument("index_name", type=str)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        from tabulate import tabulate
    except ImportError:
        print("请先安装tabulate库: pip install tabulate")
        sys.exit(1)

    client = RMIClient(args.server, debug=args.debug, use_http=args.http)

    try:
        if args.command == "status":
            status = client.query_status()
            print("\n资源状态：")
            for k, v in status.items():
                print(f"{k:>24}: {v}")

        elif args.command == "global_ddr":
            status = client.query_global_ddr_status()
            # print(status)
            print("\n全局DDR状态：")
            for k in ["total_ddr", "used_ddr", "free_ddr", "cardnum", "hostnum"]:
                print(f"{k:>16}: {status.get(k)}")
            # print_table(status.get("group_status_list", []),
            #             headers=["host", "cardid", "card_dna", "vpu_idx", "group_idx", "group_total_ddr", "group_used_ddr", "group_free_ddr"],
            #             title="Group DDR 状态")
            group_status = status.get("group_status_list", [])
            if group_status:
                print_table(group_status,
                            # headers=["host", "cardid", "card_dna", "vpu_idx", "group_idx", "group_total_ddr", "group_used_ddr", "group_free_ddr"],
                            headers="keys",
                            title="Group DDR 状态")
            # print_table(status.get("card_bar_status_list", []),
            #             headers=["host", "cardid", "free_bar_count"],
            #             title="卡BAR状态")

        elif args.command == "group_ddr":
            groups = client.query_all_group_ddr_status()
            print_table(groups,
                        # headers=["host", "cardid", "card_dna", "vpu_idx", "group_idx", "group_total_ddr", "group_used_ddr", "group_free_ddr"],
                        headers="keys",
                        title="所有Group DDR状态")

        elif args.command == "all_index_alloc":
            allocs = client.query_all_index_allocation()
            if not allocs:
                print("无索引分配信息。")
            else:
                print_table(allocs,
                            # headers=["index_name", "host", "vpu_idx", "group_idx", "chip_idx", "bank_idx",
                                    #  "column_offset", "column_length", "ddr_offset", "ddr_length", "resource_type"],
                            headers = "keys",
                            title="所有索引分配")

        elif args.command == "index_alloc":
            allocs = client.query_index_allocation(args.index_name)
            if not allocs:
                print(f"索引 {args.index_name} 无分配信息。")
            else:
                print_table(allocs,
                            # headers=["index_name", "host", "vpu_idx", "group_idx", "chip_idx", "bank_idx",
                            #          "column_range", "ddr_range", "resource_type"],
                            headers="keys",
                            title=f"索引 {args.index_name} 分配")

        elif args.command == "add_card":
            ok = client.add_card(args.host_id, args.cardid, args.card_dna)
            print("添加加速卡成功" if ok else "添加加速卡失败")

        elif args.command == "alloc_columns":
            allocs = client.allocate_columns(args.index_name, args.bytes_per_vec, args.vec_size)
            print_table(allocs,
                        # headers=["host", "vpu_idx", "group_idx", "chip_idx", "bank_idx", "column_range", "ddr_range", "type"],
                        headers="keys",
                        title="分配结果")
        elif args.command == "alloc_ddr_by_group":
            allocs = client.allocate_ddr_by_group(args.host, args.card_idx, args.group_idx, args.index_name, args.bytes_per_vec, args.vec_size)
            print_table(allocs,
                        # headers=["host", "vpu_idx", "group_idx", "chip_idx", "bank_idx", "column_range", "ddr_range", "type"],
                        headers="keys",
                        title="分配结果")

        elif args.command == "release":
            ok = client.release_columns(args.index_name)
            print("释放成功" if ok else "释放失败")

        else:
            print("未知命令")
            parser.print_help()

    except Exception as e:
        logger.error(f"操作失败: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()