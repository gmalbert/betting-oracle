import re
from pathlib import Path

path = Path(r'c:\Users\gmalb\Downloads\betting-oracle\index.html')
content = path.read_text(encoding='utf-8')

# bump icon size
content = content.replace('width: 80px;\n\t\t\theight: 80px;', 'width: 100px;\n\t\t\theight: 100px;')

# add styles for link hover inside proj-url
if '.project-tile .proj-url a {' not in content:
    content = content.replace('\t\t.project-tile .proj-url {', '\t\t.project-tile .proj-url {\n\t\t\tline-height: 1.3;\n\t\t}\n\t\t.project-tile .proj-url a {\n\t\t\tcolor: inherit;\n\t\t\ttext-decoration: none;\n\t\t}\n\t\t.project-tile .proj-url a:hover {\n\t\t\ttext-decoration: underline;\n\t\t}\n\t\t.project-tile p.proj-desc {')

pattern = re.compile(r'(<article class="project-tile">.*?<\/article>)', re.DOTALL)
changed = False


def wrap_url(match):
    global changed
    block = match.group(1)
    if '<p class="proj-url"><a ' in block:
        return block
    href_match = re.search(r'<a href="([^"]+)" target="_blank" rel="noopener noreferrer"><img', block)
    url_match = re.search(r'<p class="proj-url">(.*?)<\/p>', block, re.DOTALL)
    if href_match and url_match:
        href = href_match.group(1)
        text = url_match.group(1).strip()
        replacement = f'<p class="proj-url"><a href="{href}" target="_blank" rel="noopener noreferrer">{text}</a></p>'
        new_block = block.replace(url_match.group(0), replacement)
        changed = True
        return new_block
    return block

content = pattern.sub(wrap_url, content)

if not changed:
    raise SystemExit('No project URL replacements made')

path.write_text(content, encoding='utf-8')
print('Updated index.html')
