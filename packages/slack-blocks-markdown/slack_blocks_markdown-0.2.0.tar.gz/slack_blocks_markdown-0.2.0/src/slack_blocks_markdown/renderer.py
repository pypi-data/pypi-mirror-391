"""
Slack Blocks Renderer for Mistletoe

This module provides a custom renderer that converts Markdown to Slack Block Kit blocks.
"""

from typing import Any, cast

from mistletoe import block_token, span_token  # type: ignore[import-untyped]
from mistletoe.base_renderer import BaseRenderer  # type: ignore[import-untyped]
from slack_sdk.models.blocks import (
    Block,
    DividerBlock,
    HeaderBlock,
    MarkdownTextObject,
    PlainTextObject,
    RichTextBlock,
    SectionBlock,
)
from slack_sdk.models.blocks.block_elements import (
    RichTextElementParts,
)

from .blocks import TableBlock


class SlackBlocksRenderer(BaseRenderer):
    """
    Renderer that converts Markdown to Slack Block Kit blocks.

    Returns a list of Block objects that can be used with Slack's messaging APIs.
    """

    def __init__(self, *extras: type[Any], expand_sections: bool | None = True) -> None:
        """
        Initialize the Slack blocks renderer.

        Args:
            extras: Additional custom tokens to add to the parsing process
            expand_sections: Whether to expand all section blocks by default.
                If True (default), section blocks will always be fully expanded.
                If False, Slack may show "Show more" button for long content.
                If None, uses Slack's default behavior.
        """
        super().__init__(*extras)
        self.blocks: list[Block] = []
        self.current_text_parts: list[str] = []
        self.expand_sections = expand_sections

    def _extract_plain_text(self, token: Any) -> str:
        """
        Extract plain text from a token without any markdown formatting.

        This is used for contexts where only plain text is allowed (e.g., HeaderBlock).

        Args:
            token: The token to extract text from

        Returns:
            Plain text string without markdown formatting
        """
        # Handle raw text directly
        if isinstance(token, span_token.RawText):
            return str(token.content)

        # For formatting tokens (bold, italic, code, etc.), extract inner text
        if isinstance(
            token,
            span_token.Strong
            | span_token.Emphasis
            | span_token.Strikethrough
            | span_token.InlineCode,
        ):
            return self._extract_plain_text_from_children(token)

        # For links, extract the link text
        if isinstance(token, span_token.Link | span_token.AutoLink):
            if hasattr(token, "children") and token.children:
                return self._extract_plain_text_from_children(token)
            # For autolinks, return the URL
            return getattr(token, "target", "")

        # For images, return alt text or empty string
        if isinstance(token, span_token.Image):
            if hasattr(token, "children") and token.children:
                return self._extract_plain_text_from_children(token)
            return ""

        # For escape sequences, extract content
        if isinstance(token, span_token.EscapeSequence):
            return self._extract_plain_text_from_children(token)

        # For line breaks, return space
        if isinstance(token, span_token.LineBreak):
            return " "

        # Default: try to extract from children
        if hasattr(token, "children") and token.children:
            return self._extract_plain_text_from_children(token)

        return ""

    def _extract_plain_text_from_children(self, token: Any) -> str:
        """
        Extract plain text from all children of a token.

        Args:
            token: The token whose children to process

        Returns:
            Combined plain text from all children
        """
        parts = []
        if hasattr(token, "children") and token.children:
            for child in token.children:
                parts.append(self._extract_plain_text(child))
        return "".join(parts)

    def _render_to_rich_text_parts(  # noqa: C901
        self,
        token: Any,
        current_style: RichTextElementParts.TextStyle | None = None,
    ) -> list[dict[str, Any]]:
        """
        Convert a token and its children to RichTextElementParts.

        This recursively processes tokens and creates the appropriate rich text elements
        with proper styling (bold, italic, strikethrough, code).

        Args:
            token: The token to convert
            current_style: The accumulated TextStyle from parent tokens

        Returns:
            List of rich text element dictionaries
        """
        parts: list[dict[str, Any]] = []

        # Initialize style if needed
        if current_style is None:
            current_style = RichTextElementParts.TextStyle()

        # Handle raw text
        if isinstance(token, span_token.RawText):
            text = str(token.content)
            if text:
                text_dict: dict[str, Any] = {"type": "text", "text": text}
                # Only add style if it has any formatting
                if (
                    current_style.bold
                    or current_style.italic
                    or current_style.strike
                    or current_style.code
                ):
                    text_dict["style"] = current_style.to_dict()
                parts.append(text_dict)
            return parts

        # Handle formatting tokens - update style and recurse
        if isinstance(token, span_token.Strong):
            new_style = RichTextElementParts.TextStyle(
                bold=True,
                italic=current_style.italic,
                strike=current_style.strike,
                code=current_style.code,
            )
            if hasattr(token, "children") and token.children:
                for child in token.children:
                    parts.extend(self._render_to_rich_text_parts(child, new_style))
            return parts

        if isinstance(token, span_token.Emphasis):
            new_style = RichTextElementParts.TextStyle(
                bold=current_style.bold,
                italic=True,
                strike=current_style.strike,
                code=current_style.code,
            )
            if hasattr(token, "children") and token.children:
                for child in token.children:
                    parts.extend(self._render_to_rich_text_parts(child, new_style))
            return parts

        if isinstance(token, span_token.Strikethrough):
            new_style = RichTextElementParts.TextStyle(
                bold=current_style.bold,
                italic=current_style.italic,
                strike=True,
                code=current_style.code,
            )
            if hasattr(token, "children") and token.children:
                for child in token.children:
                    parts.extend(self._render_to_rich_text_parts(child, new_style))
            return parts

        if isinstance(token, span_token.InlineCode):
            new_style = RichTextElementParts.TextStyle(
                bold=current_style.bold,
                italic=current_style.italic,
                strike=current_style.strike,
                code=True,
            )
            if hasattr(token, "children") and token.children:
                for child in token.children:
                    parts.extend(self._render_to_rich_text_parts(child, new_style))
            return parts

        # Handle links
        if isinstance(token, span_token.Link):
            url = token.target
            # Extract link text
            link_text = ""
            if hasattr(token, "children") and token.children:
                link_text = self._extract_plain_text_from_children(token)

            link_dict: dict[str, Any] = {"type": "link", "url": url}
            if link_text and link_text != url:
                link_dict["text"] = link_text
            # Links can have style too
            if (
                current_style.bold
                or current_style.italic
                or current_style.strike
                or current_style.code
            ):
                link_dict["style"] = current_style.to_dict()
            parts.append(link_dict)
            return parts

        if isinstance(token, span_token.AutoLink):
            url = token.target
            autolink_dict: dict[str, Any] = {"type": "link", "url": url}
            if (
                current_style.bold
                or current_style.italic
                or current_style.strike
                or current_style.code
            ):
                autolink_dict["style"] = current_style.to_dict()
            parts.append(autolink_dict)
            return parts

        # Handle line breaks
        if isinstance(token, span_token.LineBreak):
            # In rich text, we represent line breaks as newline in the text
            linebreak_dict: dict[str, Any] = {"type": "text", "text": "\n"}
            if (
                current_style.bold
                or current_style.italic
                or current_style.strike
                or current_style.code
            ):
                linebreak_dict["style"] = current_style.to_dict()
            parts.append(linebreak_dict)
            return parts

        # Handle escape sequences
        if isinstance(token, span_token.EscapeSequence):
            if hasattr(token, "children") and token.children:
                for child in token.children:
                    parts.extend(self._render_to_rich_text_parts(child, current_style))
            return parts

        # Default: process children if available
        if hasattr(token, "children") and token.children:
            for child in token.children:
                parts.extend(self._render_to_rich_text_parts(child, current_style))

        return parts

    def render_document(self, token: block_token.Document) -> list[Block]:  # type: ignore[override]
        """
        Render the entire document and return the list of blocks.

        Args:
            token: The document token

        Returns:
            List of Slack Block objects
        """
        self.blocks = []
        self.render_inner(token)
        return self.blocks

    def render_heading(self, token: block_token.Heading) -> str:
        """
        Render heading as HeaderBlock.

        HeaderBlock is limited to 150 characters and only supports plain text.
        Markdown formatting is stripped since HeaderBlock doesn't support it.
        """
        # Extract plain text without markdown formatting
        text_content = self._extract_plain_text_from_children(token).strip()
        # Truncate if too long
        if len(text_content) > 150:
            text_content = text_content[:147] + "..."

        header_block = HeaderBlock(
            text=PlainTextObject(text=text_content),
        )
        self.blocks.append(header_block)
        return ""

    def render_paragraph(self, token: block_token.Paragraph) -> str:
        """
        Render paragraph as SectionBlock with MarkdownTextObject.
        """
        text_content = self.render_inner(token).strip()
        if text_content:
            # Truncate if too long (3000 char limit)
            if len(text_content) > 3000:
                text_content = text_content[:2997] + "..."

            section_block = SectionBlock(
                text=MarkdownTextObject(text=text_content),
                expand=self.expand_sections,
            )
            self.blocks.append(section_block)
        return ""

    def render_block_code(self, token: block_token.BlockCode) -> str:
        """
        Render code block as RichTextBlock with RichTextPreformattedElement.
        """
        children_list = list(token.children) if token.children else []
        code_content = getattr(children_list[0], "content", "") if children_list else ""

        if code_content:
            # Create RichTextBlock with RichTextPreformattedElement
            preformatted_element_dict = {
                "type": "rich_text_preformatted",
                "elements": [
                    {
                        "type": "text",
                        "text": code_content,
                    },
                ],
            }

            rich_text_block = RichTextBlock(elements=[preformatted_element_dict])
            self.blocks.append(rich_text_block)

        return ""

    def render_quote(self, token: block_token.Quote) -> str:
        """
        Render blockquote as RichTextBlock with RichTextQuoteElement.
        """
        # Collect rich text elements from all paragraphs within the quote
        quote_elements: list[dict[str, Any]] = []

        if token.children:
            for i, child in enumerate(token.children):
                # Process paragraph content with formatting
                if (
                    isinstance(child, block_token.Paragraph)
                    and hasattr(child, "children")
                    and child.children
                ):
                    for span_child in child.children:
                        parts = self._render_to_rich_text_parts(span_child)
                        quote_elements.extend(parts)

                    # Add line breaks between paragraphs (except after the last one)
                    if i < len(token.children) - 1:
                        quote_elements.append({"type": "text", "text": "\n"})

        if quote_elements:
            # Create RichTextBlock with RichTextQuoteElement
            quote_element_dict = {
                "type": "rich_text_quote",
                "elements": quote_elements,
            }

            rich_text_block = RichTextBlock(elements=[quote_element_dict])
            self.blocks.append(rich_text_block)

        return ""

    def render_list(  # noqa: C901
        self,
        token: block_token.List,
        indent: int = 0,
    ) -> str:
        """
        Render list as RichTextBlock with native list formatting.

        Supports nested lists by recursively handling List tokens within ListItems.

        Args:
            token: The List token to render
            indent: The indentation level for nested lists (0 for top-level)
        """
        # Determine list style
        is_ordered = hasattr(token, "start") and token.start is not None
        style = "ordered" if is_ordered else "bullet"

        # Get offset for ordered lists
        offset = None
        if is_ordered and token.start is not None:
            start_num = int(str(token.start))
            if start_num > 1:
                # offset in Slack is 0-based, so offset=1 means start at 2
                offset = start_num - 1

        # Collect list item sections and nested lists
        list_elements: list[dict[str, Any]] = []
        nested_lists: list[tuple[int, block_token.List, int]] = (
            []
        )  # (position, list_token, indent)

        if token.children:
            for child in token.children:
                list_item = cast(block_token.ListItem, child)
                # Process the list item and check for nested lists
                section_elements, _has_nested = self._render_list_item_to_rich_text(
                    list_item,
                )

                if section_elements:
                    list_elements.append(
                        {
                            "type": "rich_text_section",
                            "elements": section_elements,
                        },
                    )

                # Check for nested lists in the list item's children
                if list_item.children:
                    for child_token in list_item.children:
                        if isinstance(child_token, block_token.List):
                            # Store position where nested list should appear
                            nested_lists.append(
                                (len(list_elements), child_token, indent + 1),
                            )

        # Create the main list element
        if list_elements:
            list_element_dict: dict[str, Any] = {
                "type": "rich_text_list",
                "style": style,
                "elements": list_elements,
            }
            if indent > 0:
                # Use indent level directly (0-8 allowed by Slack)
                list_element_dict["indent"] = indent
            if offset is not None:
                list_element_dict["offset"] = offset

            # Create RichTextBlock with this list
            rich_text_block = RichTextBlock(elements=[list_element_dict])
            self.blocks.append(rich_text_block)

            # Process any nested lists
            for _, nested_list_token, nested_indent in nested_lists:
                self.render_list(nested_list_token, indent=nested_indent)

        return ""

    def _render_list_item_to_rich_text(
        self,
        token: block_token.ListItem,
    ) -> tuple[list[dict[str, Any]], bool]:
        """
        Render a list item to rich text elements.

        Returns:
            Tuple of (list of rich text element dicts, whether nested lists were found)
        """
        elements: list[dict[str, Any]] = []
        has_nested_list = False

        if token.children:
            for child in token.children:
                # Check if this is a nested list
                if isinstance(child, block_token.List):
                    has_nested_list = True
                    # Nested lists are handled separately by render_list
                    continue

                # Handle paragraphs and other inline content
                if isinstance(child, block_token.Paragraph):
                    if hasattr(child, "children") and child.children:
                        for span_child in child.children:
                            parts = self._render_to_rich_text_parts(span_child)
                            elements.extend(parts)
                else:
                    # Try to process as inline content
                    parts = self._render_to_rich_text_parts(child)
                    elements.extend(parts)

        return elements, has_nested_list

    def render_list_item(self, token: block_token.ListItem) -> str:
        """
        Legacy method for compatibility.
        This extracts the text content without creating a new block.
        """
        # List items usually contain a paragraph, get its text content
        content_parts = []
        if token.children:
            for child in token.children:
                if hasattr(child, "children") and child.children:
                    # This is typically a Paragraph, extract its text
                    for subchild in child.children:
                        content_parts.append(cast(str, self.render(subchild)))
                else:
                    content_parts.append(cast(str, self.render(child)))
        return "".join(content_parts)

    def render_thematic_break(self, token: block_token.ThematicBreak) -> str:
        """
        Render horizontal rule as DividerBlock.
        """
        divider_block = DividerBlock()
        self.blocks.append(divider_block)
        return ""

    def render_table(self, token: block_token.Table) -> str:
        """
        Render table as TableBlock with proper cell structure.
        """
        rows = []

        # Render header if present
        if hasattr(token, "header") and token.header:
            header_row = self._render_table_row_as_cells(
                cast(block_token.TableRow, token.header),
            )
            rows.append(header_row)

        # Render body rows
        if token.children:
            for row in token.children:
                body_row = self._render_table_row_as_cells(
                    cast(block_token.TableRow, row),
                )
                rows.append(body_row)

        if rows:
            # Ensure we don't exceed limits
            if len(rows) > 100:
                rows = rows[:100]

            table_block = TableBlock(rows=rows)
            self.blocks.append(table_block)
        return ""

    def _render_table_row_as_cells(
        self,
        token: block_token.TableRow,
    ) -> list[dict[str, Any]]:
        """
        Render a table row as a list of cell objects for TableBlock.

        Returns:
            List of cell objects with type and content
        """
        cells: list[dict[str, Any]] = []
        if token.children:
            for cell in token.children:
                cell_content = self.render_table_cell(cast(block_token.TableCell, cell))
                # Limit to 20 columns
                if len(cells) >= 20:
                    break
                cells.append(
                    {
                        "type": "raw_text",
                        "text": cell_content or " ",
                    },
                )
        return cells

    def render_table_row(
        self,
        token: block_token.TableRow,
        is_header: bool = False,
    ) -> str:
        """
        Render a table row.
        """
        cells = []
        if token.children:
            for cell in token.children:
                cell_content = self.render_table_cell(cast(block_token.TableCell, cell))
                cells.append(cell_content or " ")

        if is_header:
            return f"*{' | '.join(cells)}*"
        return " | ".join(cells)

    def render_table_cell(self, token: block_token.TableCell) -> str:
        """
        Render a table cell.

        Table cells use raw_text type which doesn't support markdown formatting,
        so we strip all formatting to display plain text only.
        """
        return self._extract_plain_text_from_children(token).strip()

    # Inline element renderers - these return formatted text

    def render_strong(self, token: span_token.Strong) -> str:
        """
        Render bold text with Slack markdown formatting.
        """
        content = self.render_inner(token)
        return f"*{content}*"

    def render_emphasis(self, token: span_token.Emphasis) -> str:
        """
        Render italic text with Slack markdown formatting.
        """
        content = self.render_inner(token)
        return f"_{content}_"

    def render_strikethrough(self, token: span_token.Strikethrough) -> str:
        """
        Render strikethrough text with Slack markdown formatting.
        """
        content = self.render_inner(token)
        return f"~{content}~"

    def render_inline_code(self, token: span_token.InlineCode) -> str:
        """
        Render inline code with Slack markdown formatting.
        """
        content = self.render_inner(token)
        return f"`{content}`"

    def render_link(self, token: span_token.Link) -> str:
        """
        Render link with Slack markdown formatting.
        """
        url = token.target
        text = self.render_inner(token)

        if text and text != url:
            return f"<{url}|{text}>"
        return f"<{url}>"

    def render_auto_link(self, token: span_token.AutoLink) -> str:
        """
        Render auto link with Slack markdown formatting.
        """
        return f"<{token.target}>"

    def render_image(self, token: span_token.Image) -> str:
        """
        Render image as a link (Slack blocks don't support inline images in text).
        """
        alt_text = self.render_inner(token)
        if alt_text:
            return f"<{token.src}|{alt_text}>"
        return f"<{token.src}>"

    def render_line_break(self, token: span_token.LineBreak) -> str:
        """
        Render line break.
        """
        return "\n" if token.soft else "\n\n"

    def render_raw_text(self, token: span_token.RawText) -> str:
        """
        Render raw text content.
        """
        return token.content  # type: ignore[no-any-return]

    def render_escape_sequence(self, token: span_token.EscapeSequence) -> str:
        """
        Render escaped characters.
        """
        return self.render_inner(token)  # type: ignore[no-any-return]

    def render(self, token: Any) -> list[Block] | str:
        """
        Override the base render method to handle our custom return type.
        """
        if token.__class__.__name__ == "Document":
            return self.render_document(token)
        return super().render(token)  # type: ignore[no-any-return]
