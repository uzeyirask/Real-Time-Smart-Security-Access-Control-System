from cryptography.fernet import Fernet
from tensorboard.data.proto.data_provider_pb2_grpc import add_TensorBoardDataProviderServicer_to_server
from torch.sparse import sampled_addmm

# Yeni bir anahtar oluştur
key = Fernet.generate_key()

# 'key.key' adlı bir dosya açarak (yazma modunda) şifreleme anahtarını bu dosyaya yazar.
# Eğer dosya yoksa oluşturulur, varsa üzerine yazılır.
with open('key.key', 'wb') as key_file:
    key_file.write(key)

print("Anahtar başarıyla oluşturuldu ve 'key.key' dosyasına kaydedildi.")