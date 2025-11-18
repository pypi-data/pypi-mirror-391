from core import Sesion, Tecnica, Fisica, Tactica
from queries import total_minutos, largas, filtrar_por_tipo


def main():
    s1 = Tecnica("2025-11-10", 60)
    s2 = Fisica("2025-11-12", 45)
    s3 = Sesion.desde_cadena("2025-11-14;tecnica;90")
    s4 = Tactica("2025-12-10", 100)
    try:
        s5 = Tactica("2025-12-10", 100, 1000)
    except Exception as e:
        print(f"[AVISO] Tactica -> {type(e).__name__}: {e}")
        s5 = None

    sesiones = [s for s in (s1, s2, s3, s4, s5) if s is not None]

    print("Total minutos:", total_minutos(sesiones))              # 195
    print("Largas >=60:", [s.descripcion() for s in largas(sesiones, 60)])
    print("Solo fisica:", [s.descripcion() for s in filtrar_por_tipo(sesiones, "fisica")])

    # Errores esperados (manejo de excepciones)
    malos = ["MAL;tipo;xxx", "2025-11-22;desconocido;5", "2025-11-23;fisica;-10;mas_cosas"]
    for cad in malos:
        try:
            Sesion.desde_cadena(cad)
        except Exception as e:
            print(f"OK (error controlado para {cad!r}): {type(e).__name__} → {e}")

if __name__ == "__main__":
    main()