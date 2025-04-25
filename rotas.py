import streamlit as st
import requests
import folium
from streamlit_folium import folium_static  # Correção garantida

# Função para obter coordenadas de uma cidade via OpenCage API
def obter_coordenadas_opencage(cidade):
    api_key = '736875a3f2874488b062d94c64fe4f67'  # Substitua pela sua chave de API do OpenCage
    url = f"https://api.opencagedata.com/geocode/v1/json?q={cidade}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        if dados['results']:
            coordenadas = dados['results'][0]['geometry']
            return coordenadas['lat'], coordenadas['lng']
    return None, None

# Função para calcular a rota usando a API OSRM
def calcular_rota_osrm(origem, destinos):
    origem_coords = obter_coordenadas_opencage(origem)
    destino_final_coords = obter_coordenadas_opencage(destinos[-1])

    waypoints = []
    for destino in destinos[:-1]:  
        coords = obter_coordenadas_opencage(destino)
        if coords:
            waypoints.append(f"{coords[1]},{coords[0]}")

    if origem_coords and destino_final_coords:
        base_url = "http://router.project-osrm.org/route/v1/driving/"
        waypoints_str = ";".join(waypoints) if waypoints else ""
        url = f"{base_url}{origem_coords[1]},{origem_coords[0]};{waypoints_str};{destino_final_coords[1]},{destino_final_coords[0]}?overview=full&geometries=geojson"

        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            rota = dados['routes'][0]['geometry']['coordinates']
            distancia = dados['routes'][0]['distance'] / 1000  
            duracao_em_minutos = dados['routes'][0]['duration'] / 60  

            horas = int(duracao_em_minutos // 60)
            minutos = int(duracao_em_minutos % 60)

            return {
                "origem": origem_coords,
                "destinos": [obter_coordenadas_opencage(cidade) for cidade in destinos],
                "rota": rota,
                "distancia": distancia,
                "tempo": f"{horas}h {minutos}min" if horas > 0 else f"{minutos}min"
            }
    return None

# Interface do Streamlit
st.title("🚗 Planejador de Rotas com Múltiplos Destinos")

# Entrada de cidades pelo usuário
origem = st.text_input("Cidade de Origem", "Irati, Paraná")
destinos_input = st.text_input("Cidades de Destino (separadas por vírgula)", "Palmeira, Paraná, Curitiba, Paraná")

if st.button("Calcular Rota"):
    destinos = [cidade.strip() for cidade in destinos_input.split(",")]
    
    rota_info = calcular_rota_osrm(origem, destinos)
    
    if rota_info:
        st.success(f"🔹 Distância total: {rota_info['distancia']:.2f} km")
        st.success(f"⏳ Duração estimada: {rota_info['tempo']}")

        # Criando o mapa com Folium
        mapa = folium.Map(location=rota_info["origem"], zoom_start=8)
        folium.Marker(rota_info["origem"], popup="Origem", icon=folium.Icon(color="green")).add_to(mapa)
        folium.Marker(rota_info["destinos"][-1], popup="Destino Final", icon=folium.Icon(color="red")).add_to(mapa)

        for i, cidade in enumerate(destinos[:-1]):
            folium.Marker(rota_info["destinos"][i], popup=f"Parada {i+1}: {cidade}", icon=folium.Icon(color="blue")).add_to(mapa)

        # Adicionando rota ao mapa
        rota_convertida = [(coord[1], coord[0]) for coord in rota_info["rota"]]
        folium.PolyLine(rota_convertida, color="blue", weight=5, opacity=0.8).add_to(mapa)

        # Renderizando o mapa no Streamlit
        folium_static(mapa)

    else:
        st.error("❌ Não foi possível calcular a rota. Verifique os nomes das cidades.")