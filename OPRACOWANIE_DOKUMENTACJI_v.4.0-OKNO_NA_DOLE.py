import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import glob

# Wczytaj dane z pliku Excel w bieżącym katalogu
excel_file = 'nazwa_pliku.xlsx'  # Zastąp odpowiednią nazwą pliku
df = pd.read_excel(excel_file)

# Folder zawierający obrazy TIFF
images_folder = os.path.join(os.getcwd(), 'Rysunki')

# Lista do przechowywania brakujących rysunków
missing_drawings = []

# Przejdź przez każdy wiersz w pliku Excel i zbierz uwagi dla każdego rysunku
notes_dict = {}
for index, row in df.iterrows():
    rysunek_base = row['Rysunek']
    uwagi = str(row['UWAGI'])
    anz = str(row['Anz.'])
    nazwa = str(row['NAZWA'])
    technologia = str(row['TECHNOLOGIA'])
    
    # Zmiana kolejności informacji zgodnie z żądaniem
    text_to_add = f"Nazwa: {nazwa}, Anz.: {anz}, Technologia: {technologia}, Uwagi: {uwagi}"

    # Wyszukaj pliki pasujące do wzorca 'Rysunek.tif' oraz 'Rysunek_cyfra.tif'
    exact_match = glob.glob(os.path.join(images_folder, rysunek_base + '.tif'))
    extended_match = glob.glob(os.path.join(images_folder, rysunek_base + '_*.tif'))

    # Jeśli znajdzie pasujący rysunek, wybiera go do dalszego przetwarzania
    file_path = None
    if exact_match:
        file_path = exact_match[0]  # Użyj dokładnego dopasowania, jeśli istnieje
    elif extended_match:
        file_path = extended_match[0]  # W przeciwnym razie użyj pierwszego dopasowania z dodatkowym oznaczeniem
    else:
        missing_drawings.append(rysunek_base)
        continue

    file_name = os.path.basename(file_path)
    if file_name in notes_dict:
        notes_dict[file_name].append(text_to_add)
    else:
        notes_dict[file_name] = [text_to_add]

# Dodaj uwagi do rysunków
for file_name, notes in notes_dict.items():
    original_image_path = os.path.join(images_folder, file_name)
    new_image_name = file_name.replace('.tif', '_+opracowanie.tif')
    new_image_path = os.path.join(images_folder, new_image_name)

    if os.path.isfile(original_image_path):
        with Image.open(original_image_path) as img:
            # Utwórz nowe płótno z dodatkowym miejscem na dole na tekst
            new_height = img.height + 200 * len(notes)
            combined_img = Image.new('RGB', (img.width, new_height), "white")
            combined_img.paste(img, (0, 0))
            
            draw = ImageDraw.Draw(combined_img)
            font = ImageFont.truetype('arial.ttf', 60)  # Dostosuj ścieżkę do czcionki
            
            # Rysuj każdy wpis w tabeli na dole obrazu
            y_offset = img.height
            for note in notes:
                draw.text((10, y_offset), note, fill="black", font=font)
                y_offset += 100  # Zakładając, że każdy wpis zajmuje 100 pikseli wysokości

            combined_img.save(new_image_path)
        print(f'Uwagi dodane do: {new_image_name}')
    else:
        print(f'Plik rysunku {file_name} nie istnieje w folderze Rysunki.')

# Na koniec, jeśli istnieją brakujące rysunki, zapisz ich nazwy do pliku
if missing_drawings:
    with open('brak_rysunku.txt', 'w') as f:
        for drawing in missing_drawings:
            f.write(f"{drawing}\n")
    print("Zapisano listę brakujących rysunków do pliku 'brak_rysunku.txt'.")

print("Zakończono dodawanie uwag do obrazów.")
