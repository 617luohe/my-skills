---
name: tools--文档生成
description: Word 文档创建/读取/编辑/操作全能工具。触发场景：任何提及"Word文档""word document"".docx"；生成带目录、标题、页码、信头的专业文档；提取/重组 .docx 内容；插入/替换文档中的图片；在 Word 文件中查找替换；处理修订/批注；转换为精美的 Word 文档。用户说"做个报告""写份备忘录""出一封信""做个模板"且输出为 Word/.docx 时触发。不要用于 PDF、表格、Google Docs 或与文档生成无关的编码任务。
---

# Word 文档工具

## 快速参考

| 任务 | 方法 |
|------|------|
| 读取/分析内容 | `pandoc` 或解包读原始 XML |
| 创建新文档 | 使用 `docx-js`（npm） |
| 编辑已有文档 | 解包 → 编辑 XML → 重新打包 |

### .doc 转 .docx
```bash
python scripts/office/soffice.py --headless --convert-to docx document.doc
```

### 读取内容
```bash
# 提取文本（含修订）
pandoc --track-changes=all document.docx -o output.md

# 原始 XML
python scripts/office/unpack.py document.docx unpacked/
```

### 转为图片
```bash
python scripts/office/soffice.py --headless --convert-to pdf document.docx
pdftoppm -jpeg -r 150 document.pdf page
```

## 创建新文档

用 JavaScript（docx 库）生成，然后验证：
```bash
npm install -g docx
```

```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle,
        TableOfContents, PageNumber, PageBreak } = require('docx');

const doc = new Document({ sections: [{ children: [/* 内容 */] }] });
Packer.toBuffer(doc).then(buffer => fs.writeFileSync("doc.docx", buffer));
```

创建后验证：
```bash
python scripts/office/validate.py doc.docx
```

## 编辑已有文档

1. `python scripts/office/unpack.py input.docx unpacked/`
2. 编辑 `unpacked/word/document.xml`
3. `python scripts/office/pack.py unpacked/ output.docx`

## 参考原始 skill

基于 [anthropics/skills@docx](https://github.com/anthropics/skills)，完整文件（含 scripts/）位于 `reference-skills/docx/`。
