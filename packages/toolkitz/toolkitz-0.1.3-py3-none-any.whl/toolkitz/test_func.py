

"""抓包和反编译 pyshark"""
import functools
from itertools import islice


'''

# !pip install pyshark
# 使用过滤器捕获 HTTP 流量
capture = pyshark.LiveCapture(interface="Wi-Fi", display_filter="http")

# 捕获流量，设置超时时间为50秒
capture.sniff(timeout=5)

# 打印捕获到的 HTTP 数据包
print("start")
for packet in capture:
    print(packet)
    # print('Packet Number:', packet.number)
    # print('Timestamp:', packet.sniff_time)
    # print('Source IP:', packet.ip.src)
    # print('Destination IP:', packet.ip.dst)
    time.sleep(0.1)


# 捕获网络接口上的流量
capture = pyshark.LiveCapture(interface="eth0")

# 捕获流量，设置超时时间为50秒
capture.sniff(timeout=50)

# 访问数据包内容
for packet in capture:
    print("Packet Number:", packet.number)
    print("Timestamp:", packet.sniff_time)
    print("Source IP:", packet.ip.src)
    print("Destination IP:", packet.ip.dst)
    if "http" in packet:
        print("HTTP Method:", packet.http.request_method)
        print("HTTP Host:", packet.http.host)

'''

## locust 压力测试


def struct():
    """
    一个装饰器，用于在运行时校验函数的输入参数和返回值的类型。

    此装饰器通过检查函数注解来确保传入的参数类型和函数返回值的类型符合预期。
    如果类型不匹配，将抛出 AssertionError。

    推荐在工程化项目中使用，以增强代码的健壮性和可维护性。

    用法示例:
        >>> @struct()
        >>> def add(a: int, b: int) -> int:
        >>>     return a + b
        >>> add(1, 2) # 正常执行
        3
        >>> add(1, "2") # 抛出 AssertionError

    Returns:
        Callable: 一个包装函数，用于执行类型校验。
    """

    def outer_packing(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            ann_dict = func.__annotations__

            if len(args) != 0:
                remaining_items = islice(ann_dict.items(), None, len(args))
                args_result_dict = dict(remaining_items)
                args_result_list = list(args_result_dict.values())
                try:
                    for i, j in enumerate(args_result_list):
                        assert isinstance(args[i], j)
                except AssertionError as e:
                    raise AssertionError(f"位置: {i} 预期的输入是: {j}") from e

            try:
                for k, v in kwargs.items():
                    assert isinstance(v, ann_dict[k])
            except AssertionError as e:
                raise AssertionError(f"位置: {k} 预期的输入是: {v}") from e
            try:
                assert isinstance(result, ann_dict.get("return", object))
            except AssertionError as e:
                raise AssertionError("返回值格式不准确") from e

            return result

        return wrapper

    return outer_packing


from sqlalchemy import select
from .content import create_async_session, create_async_engine
from .database import UseCase
from tqdm import tqdm
import json

import pytest


def calculate_pass_rate_and_assert(results, test_name, PASS_THRESHOLD_PERCENT = 90):
    """
    辅助函数：计算通过率并根据阈值进行断言。
    results: 包含 True (通过) 或 False (失败) 的列表
    test_name: 测试名称，用于打印信息
    """
    if not results:
        pytest.fail(f"测试 '{test_name}' 没有执行任何子用例。")

    total_sub_cases = len(results)
    passed_sub_cases = results.count(True)
    pass_rate = (passed_sub_cases / total_sub_cases) * 100

    print(f"\n--- 测试 '{test_name}' 内部结果 ---")
    print(f"总子用例数: {total_sub_cases}")
    print(f"通过子用例数: {passed_sub_cases}")
    print(f"通过率: {pass_rate:.2f}%")

    if pass_rate >= PASS_THRESHOLD_PERCENT:
        print(f"通过率 ({pass_rate:.2f}%) 达到或超过 {PASS_THRESHOLD_PERCENT}%。测试通过。")
        assert True # 显式断言成功
    else:
        print(f"通过率 ({pass_rate:.2f}%) 低于 {PASS_THRESHOLD_PERCENT}%。测试失败。")
        pytest.fail(f"测试 '{test_name}' 通过率不足 ({pass_rate:.2f}% < {PASS_THRESHOLD_PERCENT}%)")



async def atest_by_use_case(func:object,eval,PASS_THRESHOLD_PERCENT=90,
                           database_url = "mysql+aiomysql://vc_agent:aihuashen%402024@rm-2ze0q808gqplb1tz72o.mysql.rds.aliyuncs.com:3306/digital-life2",
                           limit_number = 100):

    engine = create_async_engine(database_url, 
                                 echo=False,
                                pool_size=10,        # 连接池中保持的连接数
                                max_overflow=20,     # 当pool_size不够时，允许临时创建的额外连接数
                                pool_recycle=3600,   # 每小时回收一次连接
                                pool_pre_ping=True,  # 使用前检查连接活性
                                pool_timeout=30      # 等待连接池中连接的最长时间（秒）
                                        )

    async with create_async_session(engine) as session:
        result = await session.execute(
              select(UseCase)
              .filter(UseCase.function==func.__name__)
              .order_by(UseCase.timestamp.desc())
              .limit(limit_number)
        )
        usecase = result.scalars().all()
        sub_case_results = []
        for usecase_i in tqdm(usecase):
            try:
                usecase_dict = json.loads(usecase_i.input_data)
                result = await func(**usecase_dict)
                await eval(result)
                sub_case_results.append(True)
            except AssertionError:
                sub_case_results.append(False)
                # 可以选择继续执行，或者在第一次失败时中断
                # print(f"子用例 {i} 失败，但继续执行其他子用例。")
                pass # 捕获异常，确保所有子用例都能被统计
            except Exception as e:
                sub_case_results.append(False)
                raise Exception(f"意料之外的错误 {e}")

        calculate_pass_rate_and_assert(sub_case_results, f"test_{func.__name__}_pass_{PASS_THRESHOLD_PERCENT}",PASS_THRESHOLD_PERCENT)
    