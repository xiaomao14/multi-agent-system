"""
多智能体协作系统 - 命令行入口
"""

import sys
import os
from core.graph import run_workflow
from core.config import logger


def save_result(question, result, filename=None):
    """保存结果到文件"""
    if not filename:
        safe_question = question.replace(" ", "_")[:30]
        filename = f"result_{safe_question}.txt"

    try:
        # 优先使用修订版文章，没有则使用初稿
        final_article = result.get("final_article", "")
        draft = result.get("draft", "")
        article = final_article if final_article and final_article != "没有可修订的草稿。" else draft

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"研究问题: {question}\n\n")
            f.write("=" * 60 + "\n")
            f.write("最终文章\n")
            f.write("=" * 60 + "\n")
            f.write(article)
            f.write("\n\n" + "=" * 60 + "\n")
            f.write("审稿反馈\n")
            f.write("=" * 60 + "\n")
            for fb in result.get("review_feedback", []):
                f.write(f"- {fb}\n")
        print(f"结果已保存到: {filename}")
    except Exception as e:
        logger.error(f"保存文件失败: {e}")
        print("保存失败")


def main():
    """
    多智能体协作系统命令行入口

    功能：
    - 接收用户研究问题
    - 自动执行调研 过滤 分析 写作 审稿 修订全流程
    - 显示结果和反馈
    - 支持保存结果到文件

    用法：
        python main.py

    退出：
        输入 退出、exit、quit 或 q
    """
    print("=" * 60)
    print("多智能体协作系统")
    print("=" * 60)
    print("输入你的研究问题，系统将自动完成：")
    print("   调研 过滤 分析 写作 审稿 修订")
    print("输入 help 查看帮助")
    print("输入 保存 保存当前结果")
    print("输入 退出 或 exit 结束程序")
    print("=" * 60)

    while True:
        # 获取用户输入
        question = input("\n请输入你的研究问题: ").strip()

        # 检查退出命令
        if question.lower() in ("退出", "exit", "quit", "q"):
            print("已退出程序。感谢使用！")
            break

        # 检查帮助命令
        if question.lower() in ("help", "帮助", "h"):
            print("""
帮助信息：
- 输入研究问题，系统自动完成调研->过滤->分析->写作->审稿->修订
- 输入 保存 或 save 保存当前结果到文件
- 输入 help 查看此帮助信息
- 输入 退出 或 exit 结束程序
            """)
            continue

        # 检查保存命令
        if question.lower() in ("保存", "save"):
            print("请先输入一个研究问题，然后再输入保存")
            continue

        if not question:
            print("问题不能为空，请重新输入。")
            continue

        # 显示当前问题
        print()
        print("=" * 60)
        print(f"研究问题: {question}")
        print("=" * 60)
        print("系统正在处理，请稍候...")
        print("   研究员收集资料...")

        try:
            # 执行工作流
            result = run_workflow(question)

            print("   处理完成！")
            print()

            # 优先输出修订版，没有则输出初稿
            final_article = result.get("final_article", "")
            draft = result.get("draft", "")
            article = final_article if final_article and final_article != "没有可修订的草稿。" else draft

            # 输出最终文章
            print("=" * 60)
            print("最终文章")
            print("=" * 60)
            print(article)
            print(f"\n文章长度: {len(article)} 字符")
            print()

            # 输出审稿反馈
            print("=" * 60)
            print("审稿反馈")
            print("=" * 60)
            feedback_list = result.get("review_feedback", [])
            if feedback_list:
                print(f"共 {len(feedback_list)} 条建议")
                for i, fb in enumerate(feedback_list[:10], 1):
                    print(f"  {i}. {fb}")
                if len(feedback_list) > 10:
                    print(f"  ... 还有 {len(feedback_list) - 10} 条建议")
            else:
                print("无反馈意见")
            print()

            # 输出执行日志（精简版）
            print("=" * 60)
            print("执行日志")
            print("=" * 60)
            logs = result.get("logs", [])
            if logs:
                print(f"共 {len(logs)} 条记录")
                # 只显示最近的 8 条
                for log in logs[-8:]:
                    print(f"  - {log}")
                if len(logs) > 8:
                    print(f"  ... 还有 {len(logs) - 8} 条记录")
            else:
                print("无日志记录")
            print()

            # 询问是否保存
            print("=" * 60)
            save_choice = input("是否保存结果？(y/n): ").strip().lower()
            if save_choice in ('y', 'yes'):
                save_result(question, result)
            print()

            print("=" * 60)
            print("本次任务完成！")
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n用户中断操作")
            continue
        except Exception as e:
            logger.error(f"运行失败: {e}", exc_info=True)
            print(f"\n错误: {e}")
            print("请检查网络连接或稍后重试")
            input("按回车键继续...")
            print()

    print("感谢使用，再见！")


if __name__ == "__main__":
    main()