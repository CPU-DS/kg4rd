import pandas
import tqdm
info_csv = pandas.read_csv("data/ppi/9606.protein.info.v12.0.txt", sep='\t')
print(info_csv.head())
id_to_name_list = zip(info_csv['string_protein_id'], info_csv['preferred_name'])
# print(id_to_name_list)
id_to_name_dict = dict(id_to_name_list)
# print(id_to_name_dict)
edge_file = pandas.read_csv("data/ppi/9606.protein.physical.links.v12.0.txt",sep=" ")
print(len(edge_file))

print(edge_file.keys())
protein1=edge_file["protein1"]
protein1_name = [id_to_name_dict[x] for x in protein1]
protein2=edge_file["protein2"]
protein2_name = [id_to_name_dict[x] for x in protein2]
df = pandas.DataFrame({"protein1":protein1_name,"protein2":protein2_name,"combine score":edge_file["combined_score"]})
df.to_csv("data/ppi/protein_with_name_physical.csv",index=False)
print("OK")
after = pandas.read_csv("data/ppi/protein_with_name_physical.csv")
print(len(after))
print(after.head())
ppiname = pandas.read_csv("data/ppi/protein_with_name_physical.csv")
gene_name = pandas.read_csv("data/vocab/gene_names.csv", sep="\t")
print(gene_name.head())
name_id_list = zip(gene_name["Approved symbol"],gene_name["NCBI Gene ID"])
name_id_dict = dict(name_id_list)
error = 0
nanerror = 0
x_id = []
y_id = []
x_names = []
y_names = []
for each in tqdm.tqdm(range(len(ppiname))):
    x_name = ppiname.iloc[each,0]
    y_name = ppiname.iloc[each,1]
    xid = name_id_dict.get(x_name,"ERROR")
    yid = name_id_dict.get(y_name,"ERROR")
    if xid == "ERROR" or yid=="ERROR":
        error += 1
        continue
    try:
        a = int(xid)
        b = int(yid)
    except:
        nanerror += 1
        continue
    x_id.append(int(xid))
    x_names.append(x_name)
    y_names.append(y_name)
    y_id.append(int(yid))
print(f"error: {error}")
print(f"nanerror: {nanerror}")
df = pandas.DataFrame({"proteinA_entrezid":x_id,"proteinB_entrezid":y_id,"symbolA":x_names,"symbolB":y_names})
df.to_csv("data/ppi/df_ppi_physical.csv",index=False)
print("Dataframe Complete")