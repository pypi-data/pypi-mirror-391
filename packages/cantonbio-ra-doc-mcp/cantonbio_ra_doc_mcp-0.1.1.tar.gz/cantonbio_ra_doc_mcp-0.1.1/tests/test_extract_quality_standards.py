"""
Unit tests for the extract_quality_standards module.

This test suite covers the following functionality:
- Text extraction with formatting preservation (superscript/subscript)
- Quality standards table extraction from Word documents
- Markdown table formatting

Test Categories:
1. Text formatting preservation
2. Table extraction logic
3. Markdown conversion
4. Error handling and edge cases

Test design principles:
- Use mocking to isolate external dependencies
- Cover both success and failure scenarios
- Test edge cases like empty cells, missing tables
"""

from unittest.mock import Mock, patch


from src.extract_quality_standards import (
    extract_text_with_formatting,
    extract_quality_standards_table,
    format_as_markdown_table,
    extract_quality_standards_table_from_docx
)


class TestExtractTextWithFormatting:
    """
    Test suite for extract_text_with_formatting function.

    This function extracts text from Word document cells while preserving
    superscript and subscript formatting by converting them to Unicode characters.
    """

    def test_extract_plain_text(self):
        """
        Test extraction of plain text without any formatting.

        Expected: Text should be returned as-is without modification.
        """
        mock_cell = Mock()
        mock_paragraph = Mock()
        mock_run = Mock()
        mock_run.text = "Plain text"
        mock_run.font.superscript = False
        mock_run.font.subscript = False
        mock_paragraph.runs = [mock_run]
        mock_cell.paragraphs = [mock_paragraph]

        result = extract_text_with_formatting(mock_cell)
        assert result == "Plain text"

    def test_extract_superscript_numbers(self):
        """
        Test extraction of superscript numbers.

        Expected: Superscript '2' should be converted to Unicode '²'.
        Example use case: Chemical formulas, exponents (10², m³).
        """
        mock_cell = Mock()
        mock_paragraph = Mock()
        mock_run = Mock()
        mock_run.text = "2"
        mock_run.font.superscript = True
        mock_run.font.subscript = False
        mock_paragraph.runs = [mock_run]
        mock_cell.paragraphs = [mock_paragraph]

        result = extract_text_with_formatting(mock_cell)
        assert result == "²"

    def test_extract_subscript_numbers(self):
        """
        Test extraction of subscript numbers.

        Expected: Subscript '2' should be converted to Unicode '₂'.
        Example use case: Chemical formulas (H₂O, CO₂).
        """
        mock_cell = Mock()
        mock_paragraph = Mock()
        mock_run = Mock()
        mock_run.text = "2"
        mock_run.font.superscript = False
        mock_run.font.subscript = True
        mock_paragraph.runs = [mock_run]
        mock_cell.paragraphs = [mock_paragraph]

        result = extract_text_with_formatting(mock_cell)
        assert result == "₂"

    def test_extract_mixed_formatting(self):
        """
        Test extraction of text with mixed formatting.

        Expected: Plain text and subscript should be correctly combined.
        Example: 'H' + subscript '2' = 'H₂' (hydrogen molecule).
        """
        mock_cell = Mock()
        mock_paragraph = Mock()

        mock_run1 = Mock()
        mock_run1.text = "H"
        mock_run1.font.superscript = False
        mock_run1.font.subscript = False

        mock_run2 = Mock()
        mock_run2.text = "2"
        mock_run2.font.superscript = False
        mock_run2.font.subscript = True

        mock_paragraph.runs = [mock_run1, mock_run2]
        mock_cell.paragraphs = [mock_paragraph]

        result = extract_text_with_formatting(mock_cell)
        assert result == "H₂"

    def test_extract_empty_cell(self):
        """
        Test extraction from empty cells.

        Expected: Should return empty string, not None or error.
        """
        mock_cell = Mock()
        mock_paragraph = Mock()
        mock_run = Mock()
        mock_run.text = ""
        mock_paragraph.runs = [mock_run]
        mock_cell.paragraphs = [mock_paragraph]

        result = extract_text_with_formatting(mock_cell)
        assert result == ""


class TestFormatAsMarkdownTable:
    """
    Test suite for format_as_markdown_table function.

    This function converts extracted table data into Markdown format
    with standard columns: 类型, 检验项目, 检验方法, 质量标准.
    """

    def test_format_standard_table(self):
        """
        Test formatting of a standard quality standards table.

        Expected: Should generate valid Markdown table with all columns.
        """
        table_data = [
            ['类型', '检验项目', '检验方法', '质量标准'],
            ['理化', 'pH值', '电位法', '6.0-8.0'],
            ['微生物', '无菌', '薄膜过滤法', '符合规定']
        ]

        result = format_as_markdown_table(table_data)

        assert '| 类型 | 检验项目 | 检验方法 | 质量标准 |' in result
        assert '| --- | --- | --- | --- |' in result
        assert '| 理化 | pH值 | 电位法 | 6.0-8.0 |' in result
        assert '| 微生物 | 无菌 | 薄膜过滤法 | 符合规定 |' in result

    def test_format_empty_table(self):
        """
        Test handling of empty table data.

        Expected: Should return informative message instead of empty string.
        """
        result = format_as_markdown_table([])
        assert result == "No table data found"

    def test_format_table_with_fewer_columns(self):
        """
        Test table with fewer columns than target format.

        Expected: Missing columns should be padded with empty strings.
        Edge case: Source table may not have all required columns.
        """
        table_data = [
            ['检验项目', '质量标准'],
            ['pH值', '6.0-8.0']
        ]

        result = format_as_markdown_table(table_data)

        assert '| 类型 | 检验项目 | 检验方法 | 质量标准 |' in result
        assert '| pH值 | 6.0-8.0 |  |  |' in result

    def test_format_table_with_more_columns(self):
        """
        Test table with more columns than target format.

        Expected: Extra columns should be truncated to fit target format.
        Edge case: Source table may have additional unrequired columns.
        """
        table_data = [
            ['类型', '检验项目', '检验方法', '质量标准', '备注', '其他'],
            ['理化', 'pH值', '电位法', '6.0-8.0', '常规检测', '无']
        ]

        result = format_as_markdown_table(table_data)

        lines = result.split('\n')
        assert len(lines[2].split('|')) == 6


class TestExtractQualityStandardsTable:

    @patch('src.extract_quality_standards.Document')
    def test_extract_table_with_section_43(self, mock_document_class):
        mock_doc = Mock()

        mock_paragraph = Mock()
        mock_paragraph.text = "4.3 检验项目、方法和标准"
        mock_doc.paragraphs = [mock_paragraph]

        mock_table = Mock()
        mock_row1 = Mock()
        mock_row2 = Mock()

        mock_cell1_1 = Mock()
        mock_cell1_1.paragraphs = [Mock(runs=[Mock(text='检验项目', font=Mock(superscript=False, subscript=False))])]
        mock_cell1_2 = Mock()
        mock_cell1_2.paragraphs = [Mock(runs=[Mock(text='质量标准', font=Mock(superscript=False, subscript=False))])]

        mock_cell2_1 = Mock()
        mock_cell2_1.paragraphs = [Mock(runs=[Mock(text='pH值', font=Mock(superscript=False, subscript=False))])]
        mock_cell2_2 = Mock()
        mock_cell2_2.paragraphs = [Mock(runs=[Mock(text='6.0-8.0', font=Mock(superscript=False, subscript=False))])]

        mock_row1.cells = [mock_cell1_1, mock_cell1_2]
        mock_row2.cells = [mock_cell2_1, mock_cell2_2]
        mock_table.rows = [mock_row1, mock_row2]
        mock_table.columns = [Mock(), Mock()]
        mock_doc.tables = [mock_table]

        mock_document_class.return_value = mock_doc

        result = extract_quality_standards_table("test.docx")

        assert len(result) == 2
        assert result[0] == ['检验项目', '质量标准']
        assert result[1] == ['pH值', '6.0-8.0']

    @patch('src.extract_quality_standards.Document')
    def test_extract_table_no_matching_table(self, mock_document_class):
        mock_doc = Mock()
        mock_doc.paragraphs = []
        mock_doc.tables = []

        mock_document_class.return_value = mock_doc

        result = extract_quality_standards_table("test.docx")

        assert result == []


class TestExtractQualityStandardsTableFromDocx:

    def test_successful_extraction_with_real_file(self):
        filepath = "/Users/randy/Documents/source/ra-agent-mcp/doc/example/例子-原液质量标准.docx"
        result = extract_quality_standards_table_from_docx(filepath)
        print(result)
        assert result is not None
        assert '| 类型 | 检验项目 | 检验方法 | 质量标准 |' in result

    @patch('src.extract_quality_standards.extract_quality_standards_table')
    @patch('src.extract_quality_standards.format_as_markdown_table')
    def test_successful_extraction(self, mock_format, mock_extract):
        mock_extract.return_value = [
            ['类型', '检验项目', '检验方法', '质量标准'],
            ['理化', 'pH值', '电位法', '6.0-8.0']
        ]
        mock_format.return_value = "| 类型 | 检验项目 | 检验方法 | 质量标准 |\n| --- | --- | --- | --- |\n| 理化 | pH值 | 电位法 | 6.0-8.0 |"

        result = extract_quality_standards_table_from_docx("test.docx")

        assert result is not None
        assert '| 类型 | 检验项目 | 检验方法 | 质量标准 |' in result
        mock_extract.assert_called_once_with("test.docx")
        mock_format.assert_called_once()

    @patch('src.extract_quality_standards.extract_quality_standards_table')
    def test_no_table_found(self, mock_extract):
        mock_extract.return_value = []

        result = extract_quality_standards_table_from_docx("test.docx")

        assert result is None

    @patch('src.extract_quality_standards.extract_quality_standards_table')
    def test_exception_handling(self, mock_extract):
        mock_extract.side_effect = Exception("File not found")

        result = extract_quality_standards_table_from_docx("nonexistent.docx")

        assert result is None
