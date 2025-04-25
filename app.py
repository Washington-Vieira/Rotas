import requests
import folium

def obter_coordenadas_opencage(cidade):
    """ Obtém as coordenadas da cidade usando a API OpenCage Geocoding """
    api_key = '736875a3f2874488b062d94c64fe4f67'  #  API do OpenCage
    url = f"https://api.opencagedata.com/geocode/v1/json?q={cidade}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        if dados['results']:
            coordenadas = dados['results'][0]['geometry']
            return coordenadas['lat'], coordenadas['lng']
        else:
            print(f"❌ Cidade '{cidade}' não encontrada.")
    else:
        print("❌ Erro ao acessar a API OpenCage.")
    return None, None

def calcular_rota_osrm(origem, destinos):
    """ Calcula a melhor rota passando por várias cidades usando a API OSRM e exibe no mapa """
    origem_coords = obter_coordenadas_opencage(origem)
    destino_final_coords = obter_coordenadas_opencage(destinos[-1])  # Última cidade da lista

    waypoints = []
    for destino in destinos[:-1]:  # Adiciona apenas cidades intermediárias
        coords = obter_coordenadas_opencage(destino)
        if coords:
            waypoints.append(f"{coords[1]},{coords[0]}")  # Formato longitude,latitude

    if origem_coords and destino_final_coords:
        base_url = "http://router.project-osrm.org/route/v1/driving/"
        waypoints_str = ";".join(waypoints) if waypoints else ""
        url = f"{base_url}{origem_coords[1]},{origem_coords[0]};{waypoints_str};{destino_final_coords[1]},{destino_final_coords[0]}?overview=full&geometries=geojson"

        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            rota = dados['routes'][0]['geometry']['coordinates']
            distancia = dados['routes'][0]['distance'] / 1000  # Convertendo para km
            duracao_em_minutos = dados['routes'][0]['duration'] / 60  # Convertendo para minutos

            # Convertendo minutos para horas e minutos
            horas = int(duracao_em_minutos // 60)
            minutos = int(duracao_em_minutos % 60)

            # Criando o mapa com Folium
            mapa = folium.Map(location=origem_coords, zoom_start=10)
            folium.Marker(origem_coords, popup=f"Origem: {origem}", icon=folium.Icon(color="green")).add_to(mapa)
            folium.Marker(destino_final_coords, popup=f"Destino Final: {destinos[-1]}", icon=folium.Icon(color="red")).add_to(mapa)

            for i, cidade in enumerate(destinos[:-1]):
                folium.Marker(obter_coordenadas_opencage(cidade), popup=f"Parada {i+1}: {cidade}", icon=folium.Icon(color="blue")).add_to(mapa)

            # Adicionando a rota ao mapa
            rota_convertida = [(coord[1], coord[0]) for coord in rota]  # Invertendo lat/lng
            folium.PolyLine(rota_convertida, color="blue", weight=5, opacity=0.8).add_to(mapa)

            # Exibindo informações
            print(f"\n🚗 Melhor trajeto de {origem} para {destinos[-1]}, passando por:")
            for cidade in destinos[:-1]:
                print(f"➡ {cidade}")
            print(f"\n📏 Distância total: {distancia:.2f} km")
            if horas > 0:
                print(f"⏳ Duração estimada: {horas} horas e {minutos} minutos")
            else:
                print(f"⏳ Duração estimada: {minutos} minutos")

            # Salvando o mapa
            mapa.save("rota_multidestinos.html")
            print("\n🗺️ O mapa foi salvo como 'rota_multidestinos.html'. Abra no navegador para visualizar.")

        else:
            print("❌ Erro ao calcular a rota.")
    else:
        print("❌ Não foi possível obter coordenadas de uma ou mais cidades.")

def main():
    print("🏙️ Digite os nomes das cidades para calcular a rota.")
    origem = input("Cidade de origem: ")
    destinos = input("Digite as cidades de destino separadas por vírgula: ").split(",")

    destinos = [cidade.strip() for cidade in destinos]  # Remover espaços extras

    calcular_rota_osrm(origem, destinos)

if __name__ == "__main__":
    main()