from report_out.print_clicbait_report import print_clickbait_report
from reports.clickbate_reports import clickbait_check
from scv_parser.base_parser import BaseSCVParser


def get_clickbait_report(args) -> list[list] | None:
    """проверка на кликбейт"""
    columns = ["title", 'ctr', "retention_rate"]

    results = clickbait_check(parser_param=BaseSCVParser(args.files, columns))

    if not results:
        return None

    print_clickbait_report(results, columns)
    return results
