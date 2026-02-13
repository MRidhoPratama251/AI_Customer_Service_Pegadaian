#app/service/ai_checker.py

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

def model_checker(prompt_text: str):
    llm = ChatOllama(model="qwen3-vl:235b-instruct-cloud", temperature=0.7)

    embedded_prompt = """
    Kamu adalah data auditor yang bertugas untuk memeriksa format data yang masuk sebelum di simpan ke database.

    Tugasmu :
    * mengecek format data yang masuk pastikan sama seperti di bawah ini
    {{
        \"dataOrder\": [
            {{
                \"id_percakapan\": <string>,
                \"nama_customer\": \"<harus berisi nama user tanpa angka ataupun karakter non abjad dengan huruf kapitas setiap suku katanya>\",
                \"jenis_barang\": \"televisi\" | \"handphone\" | \"kamera\" | \"laptop\" | \"emas\",
                \"nama_barang\": \"<merek_barang, contoh : emas antam | samsung a25>\",
                \"jumlah_barang\": <integer>,
                \"wilayah\": <string>,
                \"email\": <string>,
                \"estimasi_nilai_barang\": <integer>
            }}
        ]
    }}

    * nama customer tidak boleh mengandung angka atau karakter non abjad atau istilah pengganti seperti "User" | "user" | "pengguna" | <sejenisnya>
    * jenis barang hanya boleh berisi "televisi" | "handphone" | "kamera" | "laptop" | "emas"
    * nama barang harus berisi merek barang (jika emas hanya "emas antam" | "emas UBS", jika barang elektronik harus mereknya)
    * jumlah barang harus berisi integer (jika emas harus dalam satuan gram, jika barang elektronik harus jumlah unit **tidak perlu menyertakan satuan**)
    * wilayah harus berisi string 
    * estimasi nilai barang harus berisi integer
    * email harus berisi string dengan format email (domain yang diterima hanya @gmail.com)
    
    *format output yang HARUS KAMU IKUTI* :
    {{
        \"status\" : \"valid\" | \"invalid\",
        \"message\" : \"<bagian yang tidak valid>\"
    }}
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", embedded_prompt),
        ("user", "Berikut adalah data yang masuk : {topik}")
    ])

    
    chain = prompt | llm

    response = chain.invoke({"topik": prompt_text})
    
    return response.content