"""
多级内容过滤模块
提供内容去重、相关性评分、事实核查、逻辑检查等功能
"""

import hashlib
from typing import List, Dict, Tuple, Optional
from langchain_openai import ChatOpenAI
from core.config import OPENAI_MODEL, OPENAI_BASE_URL, OPENAI_API_KEY, logger


class ContentFilter:
    """内容过滤器基类"""

    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.llm = ChatOpenAI(
            model=OPENAI_MODEL,
            base_url=OPENAI_BASE_URL,
            temperature=0.1,  # 低温度保证一致性
            api_key=OPENAI_API_KEY
        )

    def filter(self, content: List[str], question: str) -> Tuple[List[str], List[str]]:
        """过滤内容，返回 (过滤后的内容, 日志列表)"""
        raise NotImplementedError


class DeduplicationFilter(ContentFilter):
    """
    过滤器1：去重 + 格式标准化

    作用：
    - 去除完全重复的内容
    - 统一空格和换行
    - 清理空字符串
    """

    def filter(self, content: List[str], question: str) -> Tuple[List[str], List[str]]:
        logger.info("过滤器1：去重启动")

        seen_hashes = set()
        unique_content = []
        original_count = len(content)

        for item in content:
            # 清理空白字符，统一格式
            cleaned = " ".join(item.split()).strip()

            if not cleaned:
                continue

            # 计算哈希值去重
            content_hash = hashlib.md5(cleaned.encode('utf-8')).hexdigest()

            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_content.append(cleaned)

        logs = [f"[去重] 从 {original_count} 条减少到 {len(unique_content)} 条"]
        logger.info("过滤器1：去重完成")

        return unique_content, logs


class RelevanceFilter(ContentFilter):
    """
    过滤器2：相关性评分

    作用：
    - 让 AI 对每条内容与问题的相关度打分（1-10分）
    - 只保留 7 分以上的内容
    - 输出每条的评分理由
    """

    def filter(self, content: List[str], question: str) -> Tuple[List[str], List[str]]:
        logger.info("过滤器2：相关性评分启动")

        if not content:
            return [], ["[相关性] 没有内容需要过滤"]

        # 构建评分 Prompt
        items_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(content)])
        prompt = f"""你是一个内容相关性评估专家。请评估以下内容与问题的相关程度。

问题：{question}

待评估内容：
{items_text}

评分标准（1-10分）：
- 10分：直接且完整地回答了问题
- 8-9分：高度相关，提供了有力支持
- 6-7分：中度相关，有一定帮助
- 4-5分：弱相关，只是边缘联系
- 1-3分：无关或几乎无关

输出格式（每条内容一行）：
[分数:X] [简要理由] 原始内容

重要：
- 评分要严格
- 只保留 7 分及以上的内容
- 每行必须包含分数、理由和原始内容
- 用中文输出理由"""

        try:
            response = self.llm.invoke(prompt)

            # 解析结果
            filtered_items = []
            logs = []
            low_score_count = 0

            for line in response.content.split("\n"):
                line = line.strip()
                if not line:
                    continue

                # 检查是否包含评分
                if "[分数:" in line:
                    try:
                        # 提取分数
                        score_start = line.index("[分数:") + 4
                        score_end = line.index("]", score_start)
                        score = int(line[score_start:score_end])

                        # 只保留高分内容
                        if score >= self.threshold * 10:
                            # 提取原始内容（去掉评分和理由）
                            original = line.split("]")[-1].strip()
                            if original:
                                filtered_items.append(original)
                                logs.append(f"[相关性] 保留(得分{score})")
                        else:
                            low_score_count += 1
                            logs.append(f"[相关性] 剔除(得分{score})")
                    except ValueError:
                        logs.append(f"[相关性] 解析失败: {line[:50]}")

            logs.insert(0, f"[相关性] 从 {len(content)} 条筛选到 {len(filtered_items)} 条，剔除 {low_score_count} 条低相关")
            logger.info("过滤器2：相关性评分完成")

            return filtered_items, logs

        except Exception as e:
            logger.error(f"相关性评分失败: {e}")
            # 失败时返回所有内容，不丢失信息
            return content, [f"[相关性] 评分出错，保留全部内容: {str(e)}"]


class FactCheckFilter(ContentFilter):
    """
    过滤器3：事实核查

    作用：
    - 检查内容是否存在明显的事实错误
    - 标记可疑数据
    - 剔除完全不可信的内容
    """

    def filter(self, content: List[str], question: str) -> Tuple[List[str], List[str]]:
        logger.info("过滤器3：事实核查启动")

        if not content:
            return [], ["[事实核查] 没有内容需要核查"]

        items_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(content)])
        prompt = f"""你是一个事实核查专家。请检查以下内容是否存在明显的事实错误或可疑之处。

问题：{question}

待核查内容：
{items_text}

核查标准：
- 可信：内容合理，无明显事实错误
- 可疑：部分内容可能不准确，需要进一步验证
- 不可信：存在明显事实错误或逻辑矛盾

输出格式（每条内容一行）：
[状态:可信/可疑/不可信] [简要理由] 原始内容

重要：
- 只对明显错误的内容标记为"不可信"
- 对于不确定的内容标记为"可疑"
- 保留可信和可疑的内容，剔除不可信的内容
- 用中文输出理由"""

        try:
            response = self.llm.invoke(prompt)

            # 解析结果
            filtered_items = []
            logs = []
            suspicious_count = 0
            unreliable_count = 0

            for line in response.content.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if "[状态:" in line:
                    try:
                        status_start = line.index("[状态:") + 4
                        status_end = line.index("]", status_start)
                        status = line[status_start:status_end]

                        original = line.split("]")[-1].strip()

                        if status == "可信":
                            if original:
                                filtered_items.append(original)
                        elif status == "可疑":
                            suspicious_count += 1
                            if original:
                                filtered_items.append(f"⚠️ 需注意: {original}")  # 标记可疑内容
                        else:
                            unreliable_count += 1
                            logs.append(f"[事实核查] 剔除不可信内容")
                    except ValueError:
                        pass

            logs.insert(0, f"[事实核查] 保留 {len(filtered_items)} 条，剔除 {unreliable_count} 条不可信，{suspicious_count} 条可疑")
            logger.info("过滤器3：事实核查完成")

            return filtered_items, logs

        except Exception as e:
            logger.error(f"事实核查失败: {e}")
            return content, [f"[事实核查] 核查出错，保留全部内容: {str(e)}"]


class LogicCheckFilter(ContentFilter):
    """
    过滤器4：逻辑检查

    作用：
    - 检查内容之间是否存在逻辑矛盾
    - 确保论述前后一致
    - 剔除自相矛盾的内容
    """

    def filter(self, content: List[str], question: str) -> Tuple[List[str], List[str]]:
        logger.info("过滤器4：逻辑检查启动")

        if len(content) < 2:
            # 内容太少，跳过逻辑检查
            return content, ["[逻辑检查] 内容不足，跳过检查"]

        items_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(content)])
        prompt = f"""你是一个逻辑分析专家。请检查以下内容之间是否存在逻辑矛盾或不一致之处。

问题：{question}

待检查内容：
{items_text}

检查标准：
- 一致：内容之间逻辑自洽，无矛盾
- 轻微矛盾：部分内容有轻微冲突，但不影响整体理解
- 严重矛盾：内容之间存在明显逻辑冲突

输出格式（每条内容一行）：
[逻辑状态:一致/轻微矛盾/严重矛盾] [简要说明] 原始内容

重要：
- 只对与其他内容有严重矛盾的内容标记
- 轻微矛盾的内容保留但加上警告标记
- 用中文输出说明"""

        try:
            response = self.llm.invoke(prompt)

            # 解析结果
            filtered_items = []
            logs = []
            conflict_count = 0

            for line in response.content.split("\n"):
                line = line.strip()
                if not line:
                    continue

                if "[逻辑状态:" in line:
                    try:
                        status_start = line.index("[逻辑状态:") + 6
                        status_end = line.index("]", status_start)
                        status = line[status_start:status_end]

                        original = line.split("]")[-1].strip()

                        if status == "一致":
                            if original:
                                filtered_items.append(original)
                        elif status == "轻微矛盾":
                            if original:
                                filtered_items.append(f"⚠️ 逻辑需注意: {original}")
                                logs.append(f"[逻辑检查] 发现轻微矛盾")
                        else:
                            conflict_count += 1
                            logs.append(f"[逻辑检查] 剔除严重矛盾内容")
                    except ValueError:
                        pass

            logs.insert(0, f"[逻辑检查] 保留 {len(filtered_items)} 条，剔除 {conflict_count} 条矛盾内容")
            logger.info("过滤器4：逻辑检查完成")

            return filtered_items, logs

        except Exception as e:
            logger.error(f"逻辑检查失败: {e}")
            return content, [f"[逻辑检查] 检查出错，保留全部内容: {str(e)}"]


class FilterPipeline:
    """
    过滤器流水线

    作用：
    - 按顺序执行多个过滤器
    - 收集所有日志
    - 支持单个过滤器失败时继续执行其他过滤器
    """

    def __init__(self, question: str, filters: Optional[List[Tuple[str, ContentFilter]]] = None):
        """
        参数：
            question: 原始研究问题（用于相关性判断）
            filters: 自定义过滤器列表，格式为 [(名称, 过滤器实例), ...]
                     默认为全部过滤器
        """
        self.question = question
        self.all_logs = []

        if filters:
            self.filters = filters
        else:
            self.filters = [
                ("去重", DeduplicationFilter()),
                ("相关性", RelevanceFilter(threshold=0.7)),
                ("事实核查", FactCheckFilter()),
                ("逻辑检查", LogicCheckFilter()),
            ]

    def execute(self, content: List[str]) -> List[str]:
        """
        执行过滤流水线

        参数：
            content: 原始内容列表

        返回：
            过滤后的内容列表
        """
        logger.info(f"开始执行过滤流水线，共 {len(self.filters)} 个过滤器")
        self.all_logs.append(f"[流水线] 开始过滤，输入 {len(content)} 条内容")

        current_content = content.copy()

        for filter_name, filter_instance in self.filters:
            try:
                logger.info(f"执行过滤器: {filter_name}")
                filtered_content, filter_logs = filter_instance.filter(current_content, self.question)

                # 合并日志
                self.all_logs.extend(filter_logs)

                # 更新当前内容
                current_content = filtered_content

                logger.info(f"过滤器 {filter_name} 完成，剩余 {len(current_content)} 条")

                # 如果内容被过滤光了，提前终止
                if not current_content:
                    self.all_logs.append(f"[流水线] 警告：{filter_name} 过滤掉了所有内容")
                    break

            except Exception as e:
                logger.error(f"过滤器 {filter_name} 执行失败: {e}")
                self.all_logs.append(f"[流水线] 过滤器 {filter_name} 出错，跳过")
                # 继续执行下一个过滤器，不中断整个流程

        self.all_logs.append(f"[流水线] 过滤完成，输出 {len(current_content)} 条内容")
        logger.info("过滤流水线执行完成")

        return current_content

    def get_logs(self) -> List[str]:
        """获取所有过滤日志"""
        return self.all_logs