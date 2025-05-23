import gradio as gr
import exifread
import PyPDF2
from mutagen import File as AudioFile
import os

def extract_metadata(file):
    extension = os.path.splitext(file.name)[-1].lower()
    result = {}
    risks = []

    if extension in [".jpg", ".jpeg", ".png"]:
        with open(file.name, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            for tag in tags:
                result[str(tag)] = str(tags[tag])
                if "GPS" in str(tag):
                    risks.append(f"⚠️ Contains GPS data: {tags[tag]}")
                if "Model" in str(tag) or "Make" in str(tag):
                    risks.append(f"📸 Device Info: {tags[tag]}")
    
    elif extension == ".pdf":
        pdf = PyPDF2.PdfReader(file.name)
        metadata = pdf.metadata
        for key in metadata:
            result[str(key)] = str(metadata[key])
            if "Author" in str(key) or "Producer" in str(key):
                risks.append(f"📝 Author Info: {metadata[key]}")
    
    elif extension in [".mp3", ".wav"]:
        audio = AudioFile(file.name)
        for key in audio:
            result[str(key)] = str(audio[key])
            if "artist" in str(key).lower() or "encoded" in str(key).lower():
                risks.append(f"🎵 Artist Info: {audio[key]}")
    
    else:
        return {"Error": "Unsupported file format."}, ""

    return result, "\n".join(risks) if risks else "✅ No obvious privacy risks detected."

iface = gr.Interface(
    fn=extract_metadata,
    inputs=gr.File(label="Upload Image / PDF / Audio"),
    outputs=["json", "text"],
    title="🔍 Metadata Privacy Risk Analyzer",
    description="Upload a file to inspect hidden metadata and identify possible privacy risks. Supports images, PDFs, and audio files."
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)))

