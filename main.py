import re
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageOps
from joblib import load
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

mlp = load(resource_path("modelo_final.joblib"))
vectorizer = load(resource_path("vetor_final.joblib"))
df = pd.read_csv(resource_path("quiz_historico_7.csv"), sep=';')

df_perguntas = df.drop_duplicates(subset="pergunta").reset_index(drop=True).head(10)

classe_para_pontuacao = {0: 0, 1: 1} 

def sem_sentido(resposta):
        resposta = resposta.lower()
        if len(set(resposta)) <= 2:  
            return True
        if re.fullmatch(r"(.)\1{4,}", resposta):  
            return True
        if not re.search(r'\b[a-zA-Z]{3,}\b', resposta):  
            return True
        return False
# ==================== CONFIGURAÇÕES GERAIS ====================
class Config:
    # Janela
    WINDOW_TITLE = "Dr. Tempus - Desafio Histórico"
    BASE_SIZE = (1920, 1080)
    MIN_SIZE = (800, 600)

    # Cores
    COLOR_WHITE = "#FFFFFF"
    COLOR_BLACK = "#000000"
    COLOR_BLUE = "#3498db"
    COLOR_RED = "#e74c3c"
    COLOR_GREEN = "#00FF00"
    COLOR_GRAY_LIGHT = "#F0F0F0"

    # Botões
    BUTTON_STYLE = {
        "font": ("Arial", 28, "bold"),
        "relief": "raised",
        "borderwidth": 3,
        "cursor": "hand2",
        "padx": 40,
        "pady": 15,
        
    }

    # Caixas de Texto
    TEXTBOX_STYLE = {
        "bg": COLOR_WHITE,
        "fg": COLOR_BLACK,
        "font": ("Arial", 12),
        "relief": "sunken",
        "borderwidth": 0,
        "padx": 5,
        "pady": 5
    }

    # Posicionamentos
    POSITIONS = {
        "tela1_button": {"relx": 0.5, "rely": 0.79, "anchor": "center"},
        "acao1": {"relx": 0.80, "rely": 0.76, "anchor": "center"},
        "acao2": {"relx": 0.80, "rely": 0.85, "anchor": "center"}
    }

    # Imagens
    IMAGES = {
        "tela1": resource_path("doutor_tempus1.png"),
        "tela2": resource_path("fundo_2.png")
    }



# ==================== GERENCIADOR DE TELAS ====================
class ScreenManager:
    def __init__(self, root):
        self.root = root
        self.current_screen = None
        self.screens = {}
        self.images = {}
        self.canvas = tk.Canvas(root, bg='black', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
    

        self._load_images()
        self._init_screens()
        self._setup_events()

        


    def _load_images(self):
        for screen, filename in Config.IMAGES.items():
            try:
                if os.path.exists(filename):
                    self.images[screen] = Image.open(filename)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar {filename}:\n{str(e)}")
                self.root.destroy()

    def _init_screens(self):
        self.screens = {
            "tela1": MainScreen(self),
            "tela2": TextScreen(self)
        }

    def _setup_events(self):
        self.root.bind('<Configure>', self._on_resize)
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.bind('<F11>', self._toggle_fullscreen)

    def show_screen(self, screen_name):
        if self.current_screen:
            self.screens[self.current_screen].cleanup()

        if screen_name in self.screens:
            self.current_screen = screen_name
            self.screens[screen_name].setup()
            self._update_display()

    def _update_display(self):
        if self.current_screen:
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            self.canvas.delete("all")
            self.screens[self.current_screen].update_display(
                width, height, self.images.get(self.current_screen))

    def _on_resize(self, event):
        if event.widget == self.root:
            self._update_display()


   
    def _toggle_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
      
    

# ==================== TELA PRINCIPAL ====================
class MainScreen:
    def __init__(self, manager):
        self.manager = manager
        self.button = None

    def setup(self):
        self.button = tk.Button(
            self.manager.root,
            text="Começar",
            command=lambda: self.manager.show_screen("tela2"),
            bg=Config.COLOR_GREEN,
            fg=Config.COLOR_WHITE,
            **Config.BUTTON_STYLE
            
        )
        pos = Config.POSITIONS["tela1_button"]
        self.button.place(
            relx=pos["relx"],
            rely=pos["rely"],
            anchor=pos["anchor"]
            
        )
        self._setup_button_effects()

    def _setup_button_effects(self):
        self.button.bind('<Enter>', lambda e: self.button.config(bg=Config.COLOR_GRAY_LIGHT))
        self.button.bind('<Leave>', lambda e: self.button.config(bg=Config.COLOR_WHITE))

    def update_display(self, width, height, image):
        if image:
            img = ImageOps.contain(image, (width, height))
            self.tk_image = ImageTk.PhotoImage(img)
            self.manager.canvas.create_image(width // 2, height // 2, image=self.tk_image)

    def cleanup(self):
        if self.button:
            self.button.place_forget()


# ==================== TELA DE TEXTO ====================
class TextScreen():
    def __init__(self, manager):
        self.manager = manager
        self.widgets = []
        self.text1 = None
        self.text2 = None
        self.label_resultado = None
        self.pergunta_atual = 0
        self.pontuacao_total = 0

    def setup(self):
        self.text1 = tk.Label(
            self.manager.root, 
            text="", 
            font=("Arial_bold", 24), 
            wraplength=700, 
            justify="center",
            bg="white"
        )
        self.text1.place(relx=0.5, rely=0.1,anchor="n", width=900, height=150)
        self.widgets.append(self.text1)

        
        self.label_resultado = tk.Label(
            self.manager.root, 
            text="", 
            font=("Arial", 14),
            bg="white"
        )
        self.label_resultado.place(relx=0.4, rely=0.28, width=300, height=30)
        self.widgets.append(self.label_resultado)

        
        self.text2 = tk.Text(self.manager.root, **Config.TEXTBOX_STYLE)
        self.text2.place(relx=0.17, rely=0.73, width=700, height=120)
        self.widgets.append(self.text2)

        
        self._create_action_buttons()
    
    
    def _create_action_buttons(self):
        style = {
            "font": ("Arial", 14, "bold"),
            "borderwidth": 3,
            "relief": "raised"
        }
       
       
        btn1 = tk.Button(
            self.manager.root,
            text="Responder",
            bg=Config.COLOR_BLUE,
            fg=Config.COLOR_WHITE,
            command=self.avaliar_resposta,
            **style
        )
        pos = Config.POSITIONS["acao1"]
        btn1.place(relx=pos["relx"], rely=pos["rely"], anchor=pos["anchor"], width=200, height=50)
        self.widgets.append(btn1)

        
        btn2 = tk.Button(
            self.manager.root,
            text="Pular",
            bg=Config.COLOR_RED,
            fg=Config.COLOR_WHITE,
            command=self.pular_pergunta,
            **style
        )
        pos = Config.POSITIONS["acao2"]
        btn2.place(relx=pos["relx"], rely=pos["rely"], anchor=pos["anchor"], width=200, height=50)
        self.widgets.append(btn2)

        self.exibir_pergunta()
    
    
    def exibir_pergunta(self):
        
        if self.pergunta_atual < len(df_perguntas):
            pergunta = df_perguntas.iloc[self.pergunta_atual]["pergunta"]
            self.text1.config(text=f"Pergunta {self.pergunta_atual + 1}: {pergunta}")
        else:
            self.finalizar_quiz()

    def avaliar_resposta(self):
        resposta_usuario = self.text2.get("1.0", tk.END).strip()
        if len(resposta_usuario) < 10:
            messagebox.showwarning("Resposta inválida", "Responda com pelo menos 10 caracteres.")
            return
        if sem_sentido(resposta_usuario):
            self.pergunta_atual += 1
            self.text2.delete("1.0", tk.END)
            self.manager.root.after(1000, self.exibir_pergunta)
            self.label_resultado.config(text=f"Pontuação: {self.pontuacao_total}")
            return



        pergunta = df_perguntas.iloc[self.pergunta_atual]["pergunta"]
        resposta_esperada = df_perguntas.iloc[self.pergunta_atual]["resposta_esperada"]

        entrada = f"{pergunta} {resposta_esperada} {resposta_usuario}"
        entrada_vetorizada = vectorizer.transform([entrada])
        classe_predita = mlp.predict(entrada_vetorizada)[0]
        pontuacao = classe_para_pontuacao.get(classe_predita, 0)

        self.pontuacao_total += pontuacao
        self.label_resultado.config(text=f"Pontuação: {self.pontuacao_total}")

        self.pergunta_atual += 1
        self.text2.delete("1.0", tk.END)
        self.manager.root.after(1000, self.exibir_pergunta)

    def pular_pergunta(self):
        self.pergunta_atual += 1
        self.text2.delete("1.0", tk.END)
        self.manager.root.after(1000, self.exibir_pergunta)
     
        
    def finalizar_quiz(self):
        self.text1.config(text=f"Quiz finalizado!\nPontuação total: {self.pontuacao_total} / {len(df_perguntas)}")
        self.text2.place_forget()
        self.label_resultado.config(text="")

        btn_restart = tk.Button(
        self.manager.root,
        text="Recomeçar",
        bg=Config.COLOR_GREEN,
        fg=Config.COLOR_WHITE,
        font=("Arial", 14, "bold"),
        command=self.recomecar_quiz
        )
        pos1 = Config.POSITIONS["acao1"]
        btn_restart.place(relx=pos1["relx"], rely=pos1["rely"], anchor=pos1["anchor"], width=200, height=50)
        self.widgets.append(btn_restart)
        

        
        btn_exit = tk.Button(
        self.manager.root,
        text="Sair",
        bg=Config.COLOR_RED,
        fg=Config.COLOR_WHITE,
        font=("Arial", 14, "bold"),
        command=self.manager.root.destroy)
        
        pos2= Config.POSITIONS["acao2"]
        btn_exit.place(relx=pos2["relx"], rely=pos2["rely"], anchor=pos2["anchor"], width=200, height=50)
        
        
        self.widgets.append(btn_exit)

    def recomecar_quiz(self):
        self.pergunta_atual = 0
        self.pontuacao_total = 0
        self.text2.delete("1.0", tk.END)
        self.text2.place(relx=0.17, rely=0.73, width=700, height=120)
        
        btn_resp = tk.Button(
        self.manager.root,
        text="Responder",
        bg=Config.COLOR_BLUE,
        fg=Config.COLOR_WHITE,
        font=("Arial", 14, "bold"),
        command=self.avaliar_resposta
        )
        btn_pular2 = tk.Button(
            self.manager.root,
            text="Pular",
            bg=Config.COLOR_RED,
            fg=Config.COLOR_WHITE,
            command=self.pular_pergunta,
            font=("Arial", 14, "bold")
        )
        pos = Config.POSITIONS["acao2"]
        btn_pular2.place(relx=pos["relx"], rely=pos["rely"], anchor=pos["anchor"], width=200, height=50)
        self.widgets.append(btn_pular2)



        pos1 = Config.POSITIONS["acao1"]
        btn_resp.place(relx=pos1["relx"], rely=pos1["rely"], anchor=pos1["anchor"], width=200, height=50)
        self.widgets.append(btn_resp)
        
        
        self.exibir_pergunta()
    

    def update_display(self, width, height, image):
        if image:
            img = ImageOps.contain(image, (width, height))
            self.tk_image = ImageTk.PhotoImage(img)
            self.manager.canvas.create_image(width // 2, height // 2, image=self.tk_image)

    def cleanup(self):
        for widget in self.widgets:
            widget.place_forget()
        self.widgets.clear()


# ==================== APLICAÇÃO PRINCIPAL ====================
def main():
    root = tk.Tk()
    root.title(Config.WINDOW_TITLE)
    root.geometry(f"{Config.BASE_SIZE[0]}x{Config.BASE_SIZE[1]}")
    root.minsize(*Config.MIN_SIZE)
    root.state('zoomed')
    root.resizable(False, False)

    try:
        manager = ScreenManager(root)
        manager.show_screen("tela1")
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro inesperado:\n{str(e)}")
    
     
if __name__ == "__main__":
    main()