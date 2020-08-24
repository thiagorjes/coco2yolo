from pycocotools.coco import COCO
import requests
import sys

# se menos que 3 da erro
if len(sys.argv) < 4 :
    print("usage:")
    print(str(sys.argv[0])+" annotation_json_path labels_dir_path images_dir_path")
    print("or")
    print(str(sys.argv[0])+" annotation_json_path labels_dir_path --download images_dir_path category_name_1,category_name_2, ... ,category_name_Nth")
    print("or")
    print(str(sys.argv[0])+" annotation_json_path labels_dir_path images_dir_path category_name_1,category_name_2, ... ,category_name_Nth")
    sys.exit(0) 

# se 3 faz tudo, mas nao baixa nada
dl_img_flag=False

annotation_json_path = sys.argv[1]
labels_dir_path = sys.argv[2]
images_dir_path = '~/Images'

coco = COCO(annotation_json_path)
cats = coco.loadCats(coco.getCatIds())

categories=[cat['name'] for cat in cats]
print(categories)
# se mais que 3...
if len(sys.argv) > 4 :
    # verifica se deve baixar e 
    # faz somente as litadas
    if sys.argv[3] == '--download' :
        dl_img_flag = True
        images_dir_path = sys.argv[4]
        if len(sys.argv)>5 :
            if len(sys.argv[5].split(","))>1 or (sys.argv[5] != "all" ) :
                categories = sys.argv[5].split(",")
    else:
        if len(sys.argv[4].split(","))>1 or sys.argv[4] != "all" :
            categories = sys.argv[4].split(",")
        
print('using '+str(len(categories))+' of 80 categories on coco')
#nms=[cat['name'] for cat in cats]

print('Selected COCO categories: \n{}\n'.format(','.join(categories)))


# Truncates numbers to N decimals
def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

catIds = []
# seleciona as category_ids das categorias selecionadas
for catnm in categories:
    catIds.extend(coco.getCatIds(catNms=[str(catnm)]))

imgIdList = []
for catid in catIds:
    # seleciona as imagens com as categorias selecionadas
    imgIdList.extend(coco.getImgIds(catIds=catid))
imgIdset = set(imgIdList)
imgIds = list(imgIdset)
#images = coco.loadImgs(imgIds) #somente imagens que tem annotations
images = coco.loadImgs(coco.getImgIds()) # todas as imagens

# baixa as imagens com as categorias selecionadas
# necessário criar o diretório ou vai dar erro
# nao quis implementar o trecho que cria o diretório (preguiça)
if dl_img_flag:
    for im in images:
        print("im: ", im['file_name'])
        img_data = requests.get(im['coco_url']).content
        with open( images_dir_path +"/"+ im['file_name'], 'wb') as handler:
            handler.write(img_data)

# salva as labels no formato da yolo para as categorias selecionadas, como a yolo precisa de ids sequenciais
# utilizo a ordem em que as categorias foram fornecidas como critério para ordenar as novas ids
for im in images:
    dw = 1. / im['width']
    dh = 1. / im['height']
    
    annIds = []
    for catid in catIds:
        annIds.extend(coco.getAnnIds(imgIds=im['id'], catIds=catid, iscrowd=False))
    anns = coco.loadAnns(annIds)
    
    filename = im['file_name'].replace(".jpg", ".txt")
    print(filename)

    with open(labels_dir_path +"/" + filename, "a") as myfile:
        for i in range(len(anns)):
            anncat = catIds.index(anns[i]["category_id"]) # nova orderm 0,1,2,3,...,Nth - será a mesma se usar as 80 classes
            xmin = anns[i]["bbox"][0]
            ymin = anns[i]["bbox"][1]
            xmax = anns[i]["bbox"][2] + anns[i]["bbox"][0]
            ymax = anns[i]["bbox"][3] + anns[i]["bbox"][1]
            
            x = (xmin + xmax)/2
            y = (ymin + ymax)/2
            
            w = xmax - xmin
            h = ymax-ymin
            
            x = x * dw
            w = w * dw
            y = y * dh
            h = h * dh
            
            # ajustado para varias categorias por imagem
            mystring = str(str(anncat)+" " + str(truncate(x, 7)) + " " + str(truncate(y, 7)) + " " + str(truncate(w, 7)) + " " + str(truncate(h, 7)))
            myfile.write(mystring)
            myfile.write("\n")

    myfile.close()
