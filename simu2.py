import numpy as np
import pandas as pd

# ================= CONFIGURACIÓN =================
HOURS = 8
SIM_TIME = HOURS * 60
REPS = 10
np.random.seed(42)

P_RET = 0.70
PROB_TIPOS = {
    "Retiro": {"R": 0.23, "N": 0.40, "L": 0.17, "ML": 0.20},
    "Pago": {"R": 0.10, "N": 0.20, "L": 0.30, "ML": 0.40},
}
MEDIA_LLEGADA = {
    "Retiro": {"R": 1, "N": 2, "L": 3, "ML": 3},
    "Pago": {"R": 1, "N": 2, "L": 3, "ML": 4},
}
MEDIA_SERVICIO = {
    "Retiro": {"R": 1, "N": 2, "L": 3, "ML": 4},
    "Pago": {"R": 3, "N": 3, "L": 5, "ML": 7},
}


def generar_usuario():
    accion = "Retiro" if np.random.rand() < P_RET else "Pago"
    tipo = np.random.choice(
        list(PROB_TIPOS[accion].keys()), p=list(PROB_TIPOS[accion].values())
    )
    inter_arr = np.random.exponential(MEDIA_LLEGADA[accion][tipo])
    serv_time = np.random.exponential(MEDIA_SERVICIO[accion][tipo])
    return accion, tipo, inter_arr, serv_time


def simular_cola(usuarios, teller_id):
    if not usuarios:
        return pd.DataFrame()
    dep_time = 0.0
    registros = []
    for u in usuarios:
        inicio_serv = max(u["arrival"], dep_time)
        espera = inicio_serv - u["arrival"]
        dep_time = inicio_serv + u["service_req"]
        registros.append(
            {
                "teller_id": teller_id,
                "action": u["action"],
                "type": u["type"],
                "wait_time": espera,
                "service_time": u["service_req"],
                "system_time": espera + u["service_req"],
            }
        )
    return pd.DataFrame(registros)


def run_simulacion(n_ret, n_pago, reps=REPS, sim_time=SIM_TIME):
    all_results = []
    for r in range(1, reps + 1):
        t = 0.0
        llegadas = []
        while t < sim_time:
            accion, tipo, inter, serv = generar_usuario()
            t += inter
            if t <= sim_time:
                llegadas.append(
                    {"action": accion, "type": tipo, "arrival": t, "service_req": serv}
                )

        cols = []
        teller_types = []

        if n_ret == 0 and n_pago == 0:
            n_tellers = 3
            cols = [[] for _ in range(n_tellers)]
            for i, u in enumerate(llegadas):
                cols[i % n_tellers].append(u)
            teller_types = ["Mixto"] * n_tellers
        else:
            retiros = [u for u in llegadas if u["action"] == "Retiro"]
            pagos = [u for u in llegadas if u["action"] == "Pago"]

            if n_ret > 0:
                cols_ret = [[] for _ in range(n_ret)]
                for i, u in enumerate(retiros):
                    cols_ret[i % n_ret].append(u)
                cols.extend(cols_ret)
                teller_types.extend(["Retiro"] * n_ret)

            if n_pago > 0:
                cols_pago = [[] for _ in range(n_pago)]
                for i, u in enumerate(pagos):
                    cols_pago[i % n_pago].append(u)
                cols.extend(cols_pago)
                teller_types.extend(["Pago"] * n_pago)

        # Procesar cada cola (M/M/1)
        for idx, col in enumerate(cols):
            df_col = simular_cola(col, f"Caja_{idx + 1}")
            if not df_col.empty:
                df_col["replica"] = r
                all_results.append(df_col)

    return pd.concat(all_results, ignore_index=True) if all_results else pd.DataFrame()


# ================= EJECUCIÓN Y ANÁLISIS =================
print("🔄 1. Ejecutando simulación base (3 cajeros mixtos)...")
df_base = run_simulacion(n_ret=0, n_pago=0)

# 1. Cajero con menor y mayor tiempo promedio de atención
stats_teller = (
    df_base.groupby("teller_id")
    .agg(
        avg_service=("service_time", "mean"),
        avg_wait=("wait_time", "mean"),
        total_users=("action", "count"),
    )
    .reset_index()
)

min_serv = stats_teller.loc[stats_teller["avg_service"].idxmin()]
max_serv = stats_teller.loc[stats_teller["avg_service"].idxmax()]
print(f"\n📊 Cajeros - Tiempo promedio de atención:")
print(stats_teller[["teller_id", "avg_service"]])
print(f"   ✅ Menor: {min_serv['teller_id']} ({min_serv['avg_service']:.2f} min)")
print(f"   ⚠️  Mayor: {max_serv['teller_id']} ({max_serv['avg_service']:.2f} min)")

# 2. Promedio de usuarios de cada tipo
avg_users_type = df_base.groupby("action").size().mean()
print(f"\n👥 Promedio de usuarios por tipo (sobre {REPS} réplicas):")
print(avg_users_type)

# 3. Total por tipo en cada réplica y modelo con menor cantidad
rep_stats = df_base.groupby("replica")["action"].value_counts().unstack(fill_value=0)
rep_stats["Total"] = rep_stats.sum(axis=1)
min_rep = rep_stats["Total"].idxmin()
print(f"\n📈 Usuarios por tipo en cada réplica:")
print(rep_stats)
print(
    f"   🔹 Réplica con menor cantidad total: R{min_rep} ({rep_stats.loc[min_rep, 'Total']} usuarios)"
)

# 4. ¿Se necesita un nuevo cajero? (Umbral: Wq > 5 min o ρ > 0.85)
overall_wait = df_base["wait_time"].mean()
overall_service = df_base["service_time"].mean()
rho = (
    overall_wait / (overall_wait + overall_service)
    if (overall_wait + overall_service) > 0
    else 0
)
necesario = overall_wait > 5.0 or rho > 0.85
print(f"\n⏱️ Evaluación de nuevo cajero:")
print(f"   - Espera promedio global: {overall_wait:.2f} min")
print(f"   - Utilización estimada (ρ): {rho:.2%}")
print(
    f"   👉 {'SÍ se recomienda agregar cajeros.' if necesario else 'NO es necesario agregar cajeros.'}"
)

# 5. Decisión de asignación exclusiva
print("\n🔍 Evaluando configuraciones dedicadas...")
configs = [(1, 2), (2, 1)]
results_configs = []
for nr, np_ in configs:
    df_conf = run_simulacion(nr, np_)
    if df_conf.empty:
        continue
    max_wq = df_conf.groupby("teller_id")["wait_time"].mean().max()
    results_configs.append(
        {
            "Config": f"{nr} Retiro / {np_} Pago",
            "Max_Wait_Q": max_wq,
            "Avg_Wait": df_conf["wait_time"].mean(),
        }
    )
df_configs = pd.DataFrame(results_configs)
if not df_configs.empty:
    optimal = df_configs.loc[df_configs["Max_Wait_Q"].idxmin()]
    print(df_configs)
    print(
        f"\n✅ Configuración óptima: {optimal['Config']} (Máxima espera en cola: {optimal['Max_Wait_Q']:.2f} min)"
    )
