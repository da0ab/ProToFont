#!/usr/bin/env python3
import fontforge
import os
import sys
import subprocess
import glob

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
    'P': 'people.svg',
    'v': 'play.svg',
    'r': 'rub.svg',
    # стрелки
    '>': 'arrow-up.svg',
    '<': 'arrow-dn.svg',
    '}': 'arrow-right.svg',
    # файлы
    'w': 'file-word.svg',  
    'p': 'file-pdf.svg',
    'd': 'file.svg',
    'x': 'file-xl.svg',
    'z': 'file-zip.svg',
}

def find_woff_converter():
    """Ищет доступные утилиты для конвертации в WOFF"""
    
    # Различные возможные имена утилит
    woff_converters = [
        'sfnt2woff-zopfli',
        'sfnt2woff',
        'woff2sfnt',
        'woff-utils'
    ]
    
    for util in woff_converters:
        try:
            # Проверяем существование утилиты
            result = subprocess.run(['which', util], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Найден конвертер WOFF: {util}")
                return util
        except:
            continue
    
    # Дополнительная проверка через whereis
    try:
        result = subprocess.run(['whereis', 'sfnt2woff'], capture_output=True, text=True)
        if result.stdout.strip() and 'sfnt2woff' in result.stdout:
            path = result.stdout.split()[1]
            print(f"✅ Найден конвертер WOFF: {path}")
            return path
    except:
        pass
    
    return None

def find_woff2_converter():
    """Ищет доступные утилиты для конвертации в WOFF2"""
    
    woff2_converters = [
        'woff2_compress',
        'woff2',
        'google-woff2'
    ]
    
    for util in woff2_converters:
        try:
            result = subprocess.run(['which', util], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Найден конвертер WOFF2: {util}")
                return util
        except:
            continue
    
    return None

def check_dependencies():
    """Проверяет наличие необходимых утилит"""
    print("\n🔍 Проверка зависимостей...")
    
    dependencies_ok = True
    
    # Проверяем FontForge
    try:
        import fontforge
        print("✅ FontForge Python модуль найден")
    except ImportError:
        print("❌ FontForge Python модуль не найден!")
        print("  Установите: sudo apt install fontforge python3-fontforge")
        dependencies_ok = False
    
    # Проверяем наличие WOFF конвертера
    woff_converter = find_woff_converter()
    if not woff_converter:
        print("⚠ Не найден конвертер для WOFF")
        print("  Будет создан только WOFF2 (если доступен)")
    
    # Проверяем наличие WOFF2 конвертера
    woff2_converter = find_woff2_converter()
    if not woff2_converter:
        print("⚠ Не найден конвертер для WOFF2")
        print("  Будет создан только WOFF (если доступен)")
    
    if not woff_converter and not woff2_converter:
        print("❌ Не найдено ни одной утилиты для конвертации!")
        print("  Установите утилиты:")
        print("  sudo apt install woff2 sfnt2woff-zopfli")
        dependencies_ok = False
    
    return dependencies_ok, woff_converter, woff2_converter

def convert_to_woff(ttf_file, output_base, woff_converter):
    """Конвертация TTF в WOFF"""
    
    woff_file = f"{output_base}.woff"
    
    if not woff_converter:
        return False
    
    try:
        if 'sfnt2woff' in woff_converter:
            # Для sfnt2woff и sfnt2woff-zopfli
            cmd = [woff_converter, ttf_file]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Проверяем созданный файл
            generated = f"{os.path.splitext(ttf_file)[0]}.woff"
            if os.path.exists(generated):
                if generated != woff_file:
                    os.rename(generated, woff_file)
                size = os.path.getsize(woff_file) / 1024
                print(f"✓ Создан WOFF: {woff_file} ({size:.1f} KB)")
                return True
        else:
            # Альтернативные методы
            print(f"⚠ Неизвестный конвертер: {woff_converter}")
            
    except subprocess.CalledProcessError as e:
        print(f"⚠ Ошибка конвертации WOFF: {e.stderr}")
    except Exception as e:
        print(f"⚠ Ошибка при создании WOFF: {e}")
    
    return False

def convert_to_woff2(ttf_file, output_base, woff2_converter):
    """Конвертация TTF в WOFF2"""
    
    woff2_file = f"{output_base}.woff2"
    
    if not woff2_converter:
        return False
    
    try:
        if 'woff2_compress' in woff2_converter:
            # Для woff2_compress
            cmd = [woff2_converter, ttf_file]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # woff2_compress создает файл с расширением .woff2
            generated = f"{ttf_file}.woff2"
            if os.path.exists(generated):
                if generated != woff2_file:
                    os.rename(generated, woff2_file)
                size = os.path.getsize(woff2_file) / 1024
                print(f"✓ Создан WOFF2: {woff2_file} ({size:.1f} KB)")
                return True
        else:
            print(f"⚠ Неизвестный конвертер: {woff2_converter}")
            
    except subprocess.CalledProcessError as e:
        print(f"⚠ Ошибка конвертации WOFF2: {e.stderr}")
    except Exception as e:
        print(f"⚠ Ошибка при создании WOFF2: {e}")
    
    return False

def generate_font_files(font, output_base, created_glyphs, woff_converter, woff2_converter):
    """Генерирует файлы шрифта"""
    
    print("\n=== Генерация файлов шрифта ===")

    # Создаем временный TTF файл
    ttf_file = f"{output_base}.ttf"
    
    try:
        # Генерируем TTF
        font.generate(ttf_file)
        print(f"✓ Создан временный TTF: {ttf_file}")
        
        if os.path.exists(ttf_file):
            size = os.path.getsize(ttf_file) / 1024
            print(f"  Размер TTF: {size:.1f} KB")
    except Exception as e:
        print(f"❌ Ошибка создания TTF: {e}")
        return False

    # Конвертируем в WOFF и WOFF2
    woff_created = convert_to_woff(ttf_file, output_base, woff_converter) if woff_converter else False
    woff2_created = convert_to_woff2(ttf_file, output_base, woff2_converter) if woff2_converter else False
    
    # Удаляем временный TTF файл
    try:
        os.remove(ttf_file)
        print(f"✓ Временный TTF файл удален")
    except Exception as e:
        print(f"⚠ Не удалось удалить TTF: {e}")

    return woff_created or woff2_created

def create_font_with_mapping(svg_dir, output_base, mapping, woff_converter, woff2_converter):
    """Создает шрифт из SVG файлов"""
    
    # Создаем новый шрифт
    font = fontforge.font()

    # Устанавливаем метаданные
    font.fontname = output_base.replace(".", "")
    font.familyname = "ProTo"
    font.fullname = "ProTo Icon Font"
    font.version = "1.0"

    # Важные метрики
    font.em = 1000
    font.ascent = 750
    font.descent = 250

    # Очищаем все глифы
    font.selection.all()
    font.clear()

    print("\n=== Создание шрифта с иконками ProTo ===")
    print(f"📁 Директория с SVG: {svg_dir}")
    print(f"📦 Имя шрифта: {output_base}")
    print("-" * 50)

    # Словарь для отслеживания созданных глифов
    created_glyphs = {}
    errors = []
    missing_files = []

    # Проверяем наличие всех SVG файлов
    print("\n🔍 Поиск SVG файлов...")
    for char, svg_file in mapping.items():
        svg_path = os.path.join(svg_dir, svg_file)
        if not os.path.exists(svg_path):
            missing_files.append(svg_file)
    
    if missing_files:
        print(f"⚠ Отсутствуют {len(missing_files)} SVG файлов:")
        for f in missing_files[:5]:
            print(f"  • {f}")
        if len(missing_files) > 5:
            print(f"  • и еще {len(missing_files) - 5}...")
    
    print("\n🔨 Создание глифов:")
    
    # Создаем глифы
    for char, svg_file in mapping.items():
        if len(char) != 1:
            continue

        # Проверяем, не создан ли уже глиф для этого символа
        if char in created_glyphs:
            print(f"⚠ Предупреждение: символ '{char}' уже создан из {created_glyphs[char]}, пропускаем {svg_file}")
            continue

        svg_path = os.path.join(svg_dir, svg_file)
        
        if not os.path.exists(svg_path):
            errors.append(f"Файл не найден: {svg_file} для символа '{char}'")
            continue

        try:
            unicode_val = ord(char)
            glyph = font.createChar(unicode_val)
            
            # Импортируем SVG
            glyph.importOutlines(svg_path)
            
            # Вычисляем ширину
            bbox = glyph.boundingBox()
            if bbox and len(bbox) >= 4:
                glyph.width = int(bbox[2]) + 50
            else:
                glyph.width = 600
            
            # Оптимизируем
            glyph.simplify()
            glyph.round()
            
            print(f"  ✓ {char} (U+{unicode_val:04X}) ← {svg_file}")
            created_glyphs[char] = svg_file
            
        except Exception as e:
            errors.append(f"Ошибка импорта {svg_file}: {e}")

    print("\n" + "=" * 50)
    print(f"✅ Создано глифов: {len(created_glyphs)}")
    if errors:
        print(f"⚠ Ошибок: {len(errors)}")
        for error in errors[:5]:
            print(f"  • {error}")
    print("=" * 50)

    if len(created_glyphs) == 0:
        print("❌ Не создано ни одного глифа!")
        return False

    # Генерируем файлы
    success = generate_font_files(font, output_base, created_glyphs, woff_converter, woff2_converter)
    
    if success:
        # Создаем CSS и HTML
        create_css_file(output_base, created_glyphs)
        create_html_demo(output_base, created_glyphs)
        print(f"\n✅ Готово! Файлы сохранены в текущей директории")
    
    return True

def create_css_file(output_base, created_glyphs):
    """Создание CSS файла"""
    
    css_content = f"""/* ProTo Icon Font */
@font-face {{
    font-family: 'ProTo';
    src: url('{output_base}.woff2') format('woff2'),
         url('{output_base}.woff') format('woff');
    font-weight: normal;
    font-style: normal;
    font-display: block;
}}

.icon {{
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
}}

/* Icon classes */
"""

    for char, svg_file in created_glyphs.items():
        class_name = os.path.splitext(svg_file)[0].lower()
        class_name = ''.join(c for c in class_name if c.isalnum() or c == '-')
        
        css_content += f"""
.icon-{class_name}:before {{
    content: "{char}";
}}
"""

    css_file = f"{output_base}.css"
    with open(css_file, "w", encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"✓ Создан CSS: {css_file}")

def create_html_demo(output_base, created_glyphs):
    """Создание HTML демо"""
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ProTo Icon Font Demo</title>
    <link rel="stylesheet" href="{output_base}.css">
    <style>
        body {{ font-family: sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #333; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 20px; margin-top: 30px; }}
        .card {{ text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
        .card:hover {{ box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .card .icon {{ font-size: 48px; color: #007bff; }}
        .card .label {{ margin-top: 10px; font-size: 14px; color: #666; }}
        .card .char {{ font-family: monospace; background: #f0f0f0; padding: 4px; border-radius: 4px; font-size: 12px; }}
        .test-area {{ margin-top: 40px; padding: 20px; background: #e3f2fd; border-radius: 8px; }}
        .test-input {{ width: 100%%; padding: 10px; font-size: 24px; font-family: 'ProTo'; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ProTo Icon Font</h1>
        <p>Всего иконок: {len(created_glyphs)}</p>
        
        <div class="grid">
"""

    for char, svg_file in created_glyphs.items():
        class_name = os.path.splitext(svg_file)[0].lower()
        class_name = ''.join(c for c in class_name if c.isalnum() or c == '-')
        
        html_content += f"""
            <div class="card">
                <div class="icon icon-{class_name}"></div>
                <div class="label">{class_name}</div>
                <div class="char">'{char}' (U+{ord(char):04X})</div>
            </div>"""

    html_content += f"""
        </div>
        
        <div class="test-area">
            <h3>Тестовая область</h3>
            <input type="text" class="test-input" id="testInput" value="VTMOR" 
                   placeholder="Введите символы (V, T, M...)">
            <div style="margin-top: 20px; font-size: 48px; font-family: 'ProTo';" id="testOutput">VTMOR</div>
        </div>
        
        <script>
            document.getElementById('testInput').addEventListener('input', function(e) {{
                document.getElementById('testOutput').textContent = e.target.value;
            }});
        </script>
    </div>
</body>
</html>"""

    html_file = f"{output_base}.html"
    with open(html_file, "w", encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Создан HTML демо: {html_file}")

def main():
    print("🔤 ProTo Icon Font Generator")
    
    # Определяем директорию с SVG
    svg_dir = "icons"
    if len(sys.argv) > 1:
        svg_dir = sys.argv[1]
    
    output_base = "ProTo"
    
    print(f"📁 Директория с SVG: {svg_dir}")
    print(f"📦 Имя шрифта: {output_base}")
    
    # Проверяем зависимости
    deps_ok, woff_converter, woff2_converter = check_dependencies()
    
    if not deps_ok:
        print("\n❌ Не все зависимости установлены!")
        print("\nУстановите необходимые пакеты:")
        print("  sudo apt update")
        print("  sudo apt install fontforge python3-fontforge woff2 sfnt2woff-zopfli")
        print("\nИли создайте символические ссылки:")
        print("  sudo ln -s /usr/bin/woff2_compress /usr/local/bin/woff2_compress")
        print("  sudo ln -s /usr/bin/sfnt2woff-zopfli /usr/local/bin/sfnt2woff")
        return
    
    # Запускаем создание шрифта
    create_font_with_mapping(svg_dir, output_base, icon_mapping, woff_converter, woff2_converter)

if __name__ == "__main__":
    main()
