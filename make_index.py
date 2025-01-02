import os
def make_index(layer_0_map, destination):
    file = open(os.path.join(destination, 'index.html'), 'w')
    file.write('<!DOCTYPE html><html><body><p>Links to downloaded webpages:</p><br>')

    for link, path in layer_0_map.items():
        local_path = os.path.relpath(path, start=destination)
        file.write('<a href="{}">{}</a><br>'.format(local_path, link))

    file.write('</body></html>')
    file.close()