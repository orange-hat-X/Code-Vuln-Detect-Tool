import sys
import os
import joblib
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QTextEdit,
    QComboBox, QPushButton, QVBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

# Model ve vectorizer'ların yükleneceği klasör
model_dir = 'models'

# Desteklenen diller
languages = ['php', 'py', 'sql']  # Eğittiğiniz dillere göre güncelleyin

# Modelleri ve vectorizer'ları yükleme
models = {}
vectorizers = {}

for lang in languages:
    vectorizer_path = os.path.join(model_dir, f'{lang}_vectorizer.pkl')
    model_path = os.path.join(model_dir, f'{lang}_model.pkl')
    
    if os.path.exists(vectorizer_path) and os.path.exists(model_path):
        vectorizers[lang] = joblib.load(vectorizer_path)
        models[lang] = joblib.load(model_path)
    else:
        print(f"{lang.upper()} model veya vectorizer bulunamadı.")

class CodeAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Güvenlik Zafiyet Analizörü")
        self.setGeometry(100, 100, 800, 300)
        
        # Layout oluşturma
        layout = QVBoxLayout()
        
        # Dil seçimi için ComboBox
        self.lang_label = QLabel("Dil Seçin:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([lang.capitalize() for lang in languages])
        
        # Kod girişi için TextEdit
        self.code_label = QLabel("Kodu Girin:")
        self.code_input = QTextEdit()
        self.code_input.setPlaceholderText("Buraya analiz etmek istediğiniz kodu yapıştırın...")
        
        # Tahmin butonu
        self.predict_button = QPushButton("Tahmin Et")
        self.predict_button.clicked.connect(self.predict_code)
        
        self.sifirla_button = QPushButton("Sıfırla")
        self.sifirla_button.clicked.connect(self.text_clear)
        
        # Sonuç etiketi
        self.result_label = QLabel("Sonuç:")
        self.result_display = QLabel("")
        self.result_display.setAlignment(Qt.AlignLeft)
        
        # Layout'a widget'ları ekleme
        layout.addWidget(self.lang_label)
        layout.addWidget(self.lang_combo)
        layout.addWidget(self.code_label)
        layout.addWidget(self.code_input)
        layout.addWidget(self.predict_button)
        layout.addWidget(self.sifirla_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.result_display)
        
        self.setLayout(layout)
    
    def text_clear(self):
        self.code_input.clear()
        self.result_display.clear()

    def predict_code(self):
        # Seçilen dili al
        selected_lang = self.lang_combo.currentText().lower()
        
        # Model ve vectorizer kontrolü
        if selected_lang not in models or selected_lang not in vectorizers:
            QMessageBox.warning(self, "Hata", f"{selected_lang.capitalize()} modeli yüklenemedi.")
            return
        
        # Kullanıcı tarafından girilen kodu al
        code = self.code_input.toPlainText().strip()
        if not code:
            QMessageBox.warning(self, "Hata", "Lütfen analiz etmek için kod girin.")
            return
        
        # Vectorizer ile kodu dönüştür
        vectorizer = vectorizers[selected_lang]
        model = models[selected_lang]
        
        try:
            code_tfidf = vectorizer.transform([code])
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kodu dönüştürürken bir hata oluştu: {e}")
            return
        
        # Model ile tahmin yap
        try:
            prediction = model.predict(code_tfidf)[0]
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Tahmin yaparken bir hata oluştu: {e}")
            return
        
        # Sonucu göster
        if prediction == 1:
            self.result_display.setText("<span style='color: red;'>Tahmin: Zararlı kod (vuln=1)</span>")
        else:
            self.result_display.setText("<span style='color: green;'>Tahmin: Zararsız kod (vuln=0)</span>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeAnalyzer()
    window.show()
    sys.exit(app.exec())
