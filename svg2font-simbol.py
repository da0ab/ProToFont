#!/usr/bin/env python3
import fontforge
import os
import sys
import subprocess

# Сопоставление букв и SVG файлов
icon_mapping = {
    'M': 'max.svg',
    'V': 'vk.svg',
    'T': 'telegram.svg',
    'O': 'ok.svg',
    'R': 'rutube.svg',
    'Y': 'youtube.svg',
    'I': 'instagram.svg',
    'F': 'facebook.svg',
    #
    'f': 'find.svg',
    'u': 'link.svg',
    'l': 'map.svg',
    'm': 'mail.svg',
    '+': 'close.svg',
    '*': 'phone-fax.svg',
    't': 'phone.svg',
    'w': 'people.svg',
    'v': 'play.svg',
    'r': 'rub.svg',
    # стрелки
    '>': 'arrow-up.svg',
    '<': 'arrow-dn.svg',
    '<': 'arrow-dn.svg',
    '}': 'arrow-right.svg',
    # файлы
    'w': 'file-word.svg',
    'p': 'file-pdf.svg',
    'D': 'file.svg',
    'x': 'file-xl.svg',
    'z': 'file-zip.svg',


}

def create_font_with_mapping(svg_dir, output_base, mapping):
    # Создаем новый шрифт
    font = fontforge.font()

    # Устанавливаем метаданные
    font.fontname = output_base.replace(".", "")
    font.familyname = "ProTo"
    font.fullname = "Custom Icon Font"
    font.version = "1.0"

    # Важные метрики
    font.em = 1000
    font.ascent = 750
    font.descent = 250

    # Очищаем все глифы
    font.selection.all()
    font.clear()

    print("=== Creating font with only custom icons ===")

    # Создаем ТОЛЬКО нужные глифы
    for char, svg_file in mapping.items():
        if len(char) == 1:
            unicode_val = ord(char)
        else:
            continue

        # Создаем глиф
        glyph = font.createChar(unicode_val)

        # Импортируем SVG
        svg_path = os.path.join(svg_dir, svg_file)
        if os.path.exists(svg_path):
            try:
                # СПОСОБ 1: Простой импорт
                glyph.importOutlines(svg_path)

                # Вычисляем ширину
                bbox = glyph.boundingBox()
                if bbox and len(bbox) >= 4:
                    # Ширина = правая граница + отступ
                    glyph.width = int(bbox[2]) + 50
                else:
                    glyph.width = 600

                # Оптимизируем контуры
                glyph.simplify()
                glyph.round()

                print(f"✓ Added: '{char}' (U+{unicode_val:04X}) ← {svg_file}")
                if bbox:
                    print(f"  Bounding box: {bbox}")
                print(f"  Width: {glyph.width}")

            except Exception as e:
                print(f"✗ Error importing {svg_file}: {e}")
                print(f"  Trying alternative import method...")

                # СПОСОБ 2: Через временный файл
                try:
                    # Создаем простой глиф как fallback
                    glyph.width = 600

                    # Рисуем простой прямоугольник с текстом
                    glyph.addPoint(100, 100)
                    glyph.addPoint(500, 100)
                    glyph.addPoint(500, 500)
                    glyph.addPoint(100, 500)
                    glyph.addPoint(100, 100)

                    print(f"  Created fallback glyph for '{char}'")
                except:
                    print(f"  Could not create fallback for '{char}'")
        else:
            print(f"✗ Warning: {svg_file} not found!")
            glyph.width = 600

    print(f"\n=== Generating font files ===")

    # Создаем базовый TTF
    ttf_file = f"{output_base}.ttf"
    try:
        # Упрощенные флаги для старой версии FontForge
        font.generate(ttf_file)
        print(f"✓ Created: {ttf_file}")

        # Проверяем размер файла
        if os.path.exists(ttf_file):
            size = os.path.getsize(ttf_file) / 1024
            print(f"  File size: {size:.1f} KB")
        else:
            print(f"✗ Error: TTF file not created")
            return

    except Exception as e:
        print(f"✗ Error generating TTF: {e}")
        return

    # Конвертируем в WOFF и WOFF2 с помощью внешних утилит
    if convert_to_woff(ttf_file, output_base):
        print(f"\n=== All formats generated successfully ===")
    else:
        print(f"\n=== Only TTF generated (install woff tools for more formats) ===")

    # Создаем CSS файл
    create_css_file(output_base, mapping)

    # Показываем информацию о шрифте
    show_font_info(ttf_file)

def convert_to_woff(ttf_file, output_base):
    """Конвертация в WOFF/WOFF2 с помощью внешних утилит"""

    woff_created = False
    woff2_created = False

    # 1. Конвертация в WOFF (если есть sfnt2woff)
    woff_file = f"{output_base}.woff"
    try:
        # Проверяем доступность sfnt2woff
        result = subprocess.run(["which", "sfnt2woff"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run(["sfnt2woff", ttf_file], check=True)

            # Проверяем что файл создан
            if os.path.exists(woff_file):
                woff_created = True
                size = os.path.getsize(woff_file) / 1024
                print(f"✓ Created: {woff_file} ({size:.1f} KB)")
            else:
                # Пробуем переименовать
                base_name = os.path.splitext(ttf_file)[0]
                if os.path.exists(f"{base_name}.woff"):
                    os.rename(f"{base_name}.woff", woff_file)
                    woff_created = True
                    size = os.path.getsize(woff_file) / 1024
                    print(f"✓ Created: {woff_file} ({size:.1f} KB)")
    except Exception as e:
        print(f"⚠ Could not create WOFF: {e}")

    # 2. Конвертация в WOFF2 (если есть woff2_compress)
    woff2_file = f"{output_base}.woff2"
    try:
        # Проверяем доступность woff2_compress
        result = subprocess.run(["which", "woff2_compress"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            subprocess.run(["woff2_compress", ttf_file], check=True)

            # Проверяем что файл создан
            if os.path.exists(woff2_file):
                woff2_created = True
                size = os.path.getsize(woff2_file) / 1024
                print(f"✓ Created: {woff2_file} ({size:.1f} KB)")
            else:
                # Пробуем найти в текущей директории
                base_name = os.path.splitext(ttf_file)[0]
                if os.path.exists(f"{base_name}.woff2"):
                    os.rename(f"{base_name}.woff2", woff2_file)
                    woff2_created = True
                    size = os.path.getsize(woff2_file) / 1024
                    print(f"✓ Created: {woff2_file} ({size:.1f} KB)")
    except Exception as e:
        print(f"⚠ Could not create WOFF2: {e}")

    return woff_created or woff2_created

def create_css_file(output_base, mapping):
    """Создание CSS файла"""

    css_content = f"""/* Custom Icon Font - Generated {output_base} */
@font-face {{
    font-family: 'ProTo';
    src: url('{output_base}.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
    font-display: block;
}}
"""

    # Добавляем WOFF и WOFF2 если они существуют
    extra_src = []
    if os.path.exists(f"{output_base}.woff"):
        extra_src.append(f"url('{output_base}.woff') format('woff')")
    if os.path.exists(f"{output_base}.woff2"):
        extra_src.append(f"url('{output_base}.woff2') format('woff2')")

    if extra_src:
        css_content = css_content.replace(
            "src: url('{output_base}.ttf') format('truetype');",
            "src: url('{output_base}.ttf') format('truetype'),\n         " +
            ",\n         ".join(extra_src) + ";"
        )

    css_content += """
.icon {
    font-family: 'ProTo' !important;
    speak: never;
    font-style: normal;
    font-weight: normal;
    font-variant: normal;
    text-transform: none;
    line-height: 1;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    display: inline-block;
}

/* Individual icon classes */
"""

    for char, svg_file in mapping.items():
        if len(char) == 1:
            # Создаем имя класса из имени файла без расширения
            class_name = os.path.splitext(svg_file)[0]
            # Заменяем недопустимые символы в имени класса
            class_name = ''.join(c for c in class_name if c.isalnum() or c in '_-')
            if not class_name[0].isalpha():
                class_name = 'icon-' + class_name

            css_content += f""".{class_name}:before {{
    content: "{char}";
}}

"""

    css_file = f"{output_base}.css"
    with open(css_file, "w") as f:
        f.write(css_content)

    print(f"✓ Created: {css_file}")

    # Создаем простой HTML для демонстрации
    create_simple_demo(output_base, mapping)

def create_simple_demo(output_base, mapping):
    """Создание простого HTML демо"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{output_base} Icon Font Demo</title>
    <link rel="stylesheet" href="{output_base}.css">
    <style>
        body {{ font-family: sans-serif; margin: 40px; }}
        .demo {{ margin: 20px 0; }}
        .icon {{ font-size: 32px; margin: 10px; color: #007bff; }}
        .code {{ font-family: monospace; background: #f0f0f0; padding: 5px; margin: 5px; }}
        table {{ border-collapse: collapse; width: 100%%; }}
        td, th {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>{output_base} Icon Font Demo</h1>

    <table>
        <tr>
            <th>Icon</th>
            <th>Character</th>
            <th>Unicode</th>
            <th>Class</th>
            <th>SVG File</th>
            <th>HTML Code</th>
        </tr>
"""

    for char, svg_file in mapping.items():
        if len(char) == 1:
            class_name = os.path.splitext(svg_file)[0]
            class_name = ''.join(c for c in class_name if c.isalnum() or c in '_-')
            if not class_name[0].isalpha():
                class_name = 'icon-' + class_name

            unicode_hex = f"U+{ord(char):04X}"
            html_code = f"&amp;#{ord(char)};"

            html_content += f"""
        <tr>
            <td><span class="icon {class_name}"></span></td>
            <td>'{char}'</td>
            <td>{unicode_hex}</td>
            <td><code>.{class_name}</code></td>
            <td>{svg_file}</td>
            <td><code>{html_code}</code></td>
        </tr>"""

    html_content += """
    </table>

    <div class="demo">
        <h3>Usage Examples:</h3>
        <div class="code">&lt;i class="icon max"&gt;&lt;/i&gt;</div>
        <div class="code">&lt;span style="font-family: 'ProTo'"&gt;M&lt;/span&gt;</div>
    </div>

    <div class="demo">
        <h3>Test Area:</h3>
        <input type="text" id="test-text" placeholder="Type M or b here..."
               style="font-family: 'ProTo', sans-serif; font-size: 24px; padding: 10px; width: 300px;">
        <div id="test-output" style="margin-top: 10px; font-family: 'ProTo'; font-size: 32px;"></div>
    </div>

    <script>
        document.getElementById('test-text').addEventListener('input', function(e) {{
            document.getElementById('test-output').textContent = e.target.value;
        }});
    </script>
</body>
</html>
"""

    html_file = f"{output_base}.html"
    with open(html_file, "w") as f:
        f.write(html_content)

    print(f"✓ Created: {html_file}")

def show_font_info(ttf_file):
    """Показывает информацию о созданном шрифте"""

    if os.path.exists(ttf_file):
        try:
            # Используем ttx для получения информации
            result = subprocess.run(["ttx", "-l", ttf_file],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("\n=== Font Information ===")
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Glyph' in line or 'tables' in line:
                        print(line)
        except:
            # Альтернатива: через fc-query
            try:
                result = subprocess.run(["fc-query", ttf_file],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("\n=== Font Information ===")
                    for line in result.stdout.split('\n')[:10]:
                        if 'family:' in line or 'style:' in line or 'glyphs:' in line:
                            print(line.strip())
            except:
                pass

if __name__ == "__main__":
    # Установите правильные пути
    svg_dir = "./icons"  # Папка с SVG
    output_name = "myfont"  # Имя шрифта (без расширения)

    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        svg_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_name = sys.argv[2]

    # Создаем папку для SVG если её нет
    if not os.path.exists(svg_dir):
        os.makedirs(svg_dir, exist_ok=True)
        print(f"Created directory: {svg_dir}")
        print("Please add your SVG files to this directory and update icon_mapping")

    # Запускаем создание шрифта
    create_font_with_mapping(
        svg_dir=svg_dir,
        output_base=output_name,
        mapping=icon_mapping
    )
