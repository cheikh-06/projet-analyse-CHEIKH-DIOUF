import pandas as pd
import matplotlib.pyplot as plt
import json, os, sys

csv_path = "data/logs_reseau.csv"
if not os.path.exists(csv_path):
    csv_path = "logs_reseau.csv"

print(f"Chargement {csv_path}...")
df = pd.read_csv(csv_path)
print(f"Initial: {len(df)} lignes")

df = df.drop_duplicates()
df['protocol'] = df['protocol'].astype(str).str.upper()
med = df['bytes_sent'].median()
df['bytes_sent'] = df['bytes_sent'].fillna(med)

top_port = int(df['dst_port'].mode().iloc[0])
taux_deny = round((df['action']=='DENY').mean()*100,2)
ip_scanner = str(df.groupby('src_ip')['dst_port'].nunique().idxmax())
ip_exfil = str(df.groupby('src_ip')['bytes_sent'].sum().idxmax())

resultats = {
  "nb_lignes_apres_nettoyage": int(len(df)),
  "top_port": top_port,
  "taux_deny_pct": float(taux_deny),
  "ip_scanner": ip_scanner,
  "ip_exfiltration": ip_exfil
}

os.makedirs("figures", exist_ok=True)
with open("resultats.json","w",encoding="utf-8") as f:
    json.dump(resultats,f,indent=2,ensure_ascii=False)

df['dst_port'].value_counts().head(10).plot(kind='bar')
plt.title('Top 10 ports destination'); plt.xlabel('Port'); plt.ylabel('Connexions')
plt.tight_layout(); plt.savefig('figures/top_ports.png',dpi=150); plt.close()

df['action'].value_counts().plot(kind='bar',color=['green','red'])
plt.title('ALLOW vs DENY'); plt.tight_layout(); plt.savefig('figures/allow_deny.png',dpi=150); plt.close()

df.groupby('device_type')['bytes_sent'].sum().sort_values(ascending=False).plot(kind='bar')
plt.title('Volume octets par type'); plt.tight_layout(); plt.savefig('figures/bytes_par_device.png',dpi=150); plt.close()

print("OK RESULTAT:")
print(resultats)
