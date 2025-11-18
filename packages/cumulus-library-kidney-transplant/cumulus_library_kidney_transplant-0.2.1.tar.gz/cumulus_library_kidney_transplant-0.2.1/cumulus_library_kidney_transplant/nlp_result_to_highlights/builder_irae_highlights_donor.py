"""Module for generating age ranges table from NLP"""

import pathlib

import cumulus_library
from cumulus_library import base_utils, databases
from cumulus_library.template_sql import sql_utils


class IraeNlpHighlightsDonorBuilder(cumulus_library.BaseTableBuilder):
    display_text = "Transforming donor IRAE NLP results into a table of highlights..."

    @staticmethod
    def _is_table_valid(database: databases.DatabaseBackend, table_name: str) -> bool:
        return sql_utils.is_field_present(
            database=database,
            source_table=table_name,
            source_col="result",
            expected={},
        )

    def _get_valid_irae_nlp_tables(self, database: databases.DatabaseBackend) -> set[str]:
        source_tables = [
            "irae__nlp_donor_gpt4o",
            "irae__nlp_donor_gpt5",
            "irae__nlp_donor_gpt_oss_120b",
            "irae__nlp_donor_llama4_scout",
            "irae__nlp_donor_claude_sonnet45",
        ]
        valid_tables = set()
        with base_utils.get_progress_bar() as progress:
            task = progress.add_task(
                "Discovering available NLP tables for donor IRAE variables...",
                total=len(source_tables),
            )
            for source_table in source_tables:
                if self._is_table_valid(database, source_table):
                    valid_tables.add(source_table)
                progress.advance(task)
        return valid_tables

    def prepare_queries(
        self,
        *args,
        config: cumulus_library.StudyConfig,
        **kwargs,
    ):
        valid_tables = self._get_valid_irae_nlp_tables(config.db)
        query = cumulus_library.get_template(
            "irae__highlights_donor",
            pathlib.Path(__file__).parent,
            table_names=valid_tables,
        )
        self.queries.append(query)
