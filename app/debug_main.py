print("=== DEBUG MAIN ===")
print("1. Testando import do FastAPI...")

try:
    from fastapi import FastAPI
    print("✅ FastAPI importado com sucesso")
except Exception as e:
    print(f"❌ Erro no import FastAPI: {e}")
    exit()

print("2. Criando app...")

try:
    app = FastAPI(title="Teste Debug")
    print("✅ App criado com sucesso")
except Exception as e:
    print(f"❌ Erro ao criar app: {e}")
    exit()

print("3. Definindo rotas...")

@app.get("/")
def root():
    return {"message": "debug funcionando"}

print("✅ Rotas definidas")
print("4. App pronto:", app)