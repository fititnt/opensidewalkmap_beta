import folium

bounding_box = (-25.46340831586,-49.26485433156466,-25.45836407828201,-49.257818266840495)

mid_lat = (bounding_box[0]+bounding_box[2])/2
mid_lgt = (bounding_box[1]+bounding_box[3])/2




m = folium.Map(location=[mid_lat, mid_lgt],zoom_start=18)


m.save("index.html")