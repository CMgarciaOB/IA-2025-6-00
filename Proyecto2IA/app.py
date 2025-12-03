import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import uuid
import threading
import cv2
from PIL import Image, ImageTk
from models.ocr_model import htr_pipeline
from models.tts_model import tts_pipeline
from models.utils import postprocess_text


class OCRtoVoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Transformador a Voz")
        self.root.geometry("600x350")
        
        os.makedirs('uploads', exist_ok=True)
        os.makedirs('audio', exist_ok=True)
        
        self.image_path = None
        self.audio_path = None
        self.camera = None
        
        # Botón paraabrir la opcion de tomar foto
        self.camera_btn = tk.Button(
            root, 
            text="Tomar Foto y Procesar", 
            command=self.take_photo,
            font=("sans-serif", 14, "bold"),
            bg="#00ff3c",
            fg="white",
            height=2
        )
        self.camera_btn.pack(pady=(20,5), padx=20, fill="both", expand=True)
        
        # Botón para seleccionar imagen desde archivos
        self.process_btn = tk.Button(
            root, 
            text="Seleccionar Imagen", 
            command=self.process,
            font=("sans-serif", 14, "bold"),
            bg="#0a75e9",
            fg="white",
            height=2
        )
        self.process_btn.pack(pady=5, padx=20, fill="both", expand=True)
        
        # Progress bar nomas pa que se vea elegante
        self.progress = ttk.Progressbar(root, mode='indeterminate')
        self.progress.pack(pady=10, padx=20, fill="x")
    
    def take_photo(self):
        """Capturar foto desde la cámara"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("Error", "No se pudo acceder a la cámara")
                return
            
            # Ventana de captura de texto
            capture_window = tk.Toplevel(self.root)
            capture_window.title("Capturar Foto")
            capture_window.geometry("640x520")
            
            video_label = tk.Label(capture_window)
            video_label.pack()
            
            def update_frame():
                ret, frame = self.camera.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img = img.resize((640, 480))
                    imgtk = ImageTk.PhotoImage(image=img)
                    video_label.imgtk = imgtk
                    video_label.configure(image=imgtk)
                    video_label.after(10, update_frame)
            
            def capture():
                ret, frame = self.camera.read()
                if ret:
                    # Guardar la foto
                    photo_path = os.path.join('uploads', str(uuid.uuid4()) + '.jpg')
                    cv2.imwrite(photo_path, frame)
                    self.image_path = photo_path
                    
                    # Cerrar la interfaz de la camara
                    self.camera.release()
                    capture_window.destroy()
                    
                    # Procesar la imagen
                    self.camera_btn.config(state=tk.DISABLED)
                    self.process_btn.config(state=tk.DISABLED)
                    threading.Thread(target=self.run_pipeline, daemon=True).start()
            
            def close_camera():
                self.camera.release()
                capture_window.destroy()
            
            # Botón para capturar la foto
            btn_frame = tk.Frame(capture_window)
            btn_frame.pack(pady=10)
            
            capture_btn = tk.Button(btn_frame, text="Capturar", command=capture, 
                                   bg="#28a745", fg="white", font=("Arial", 12, "bold"))
            capture_btn.pack(side=tk.LEFT, padx=5)
            
            cancel_btn = tk.Button(btn_frame, text="Cancelar", command=close_camera,
                                  bg="#dc3545", fg="white", font=("Arial", 12, "bold"))
            cancel_btn.pack(side=tk.LEFT, padx=5)
            
            capture_window.protocol("WM_DELETE_WINDOW", close_camera)
            update_frame()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al acceder a la cámara: {str(e)}")
    
    def process(self):
        """Seleccionar imagen, procesar y reproducir audio"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if not file_path:
            return
        
        self.image_path = file_path
        self.camera_btn.config(state=tk.DISABLED)
        self.process_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.run_pipeline, daemon=True).start()
    
    def run_pipeline(self):
        """Ejecutar todo el pipeline"""
        try:
            self.progress.start(10)
            
            # Copiar la imagen temporal
            temp_path = os.path.join('uploads', str(uuid.uuid4()) + os.path.splitext(self.image_path)[1])
            with open(self.image_path, 'rb') as src, open(temp_path, 'wb') as dst:
                dst.write(src.read())
            
            # Transcribir y procesar
            transcribed = htr_pipeline.transcribe(temp_path)
            final_text = postprocess_text(transcribed)
            
            # Generar el audio normalizado
            audio_path = os.path.join('audio', str(uuid.uuid4()) + ".mp3")
            self.audio_path = tts_pipeline.synthesize(final_text, audio_path, voice="es-MX-JorgeNeural")
            
            # Limpiar el archivo temporal
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            # Reproducir el audio
            if self.audio_path and os.path.exists(self.audio_path):
                os.startfile(self.audio_path)
                self.root.after(0, lambda: messagebox.showinfo("Audio generado y en reproduccion"))
            else:
                raise Exception("No se pudo procesar")
                
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        finally:
            self.progress.stop()
            self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL))


if __name__ == '__main__':
    root = tk.Tk()
    app = OCRtoVoiceApp(root)
    root.mainloop()
