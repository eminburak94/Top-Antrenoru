# Konumsal maç motoru

saha_motoru.py içindeki PitchState, dizilişten türeyen sabit başlangıç alanlarını, oyuncu koordinatlarını, topu, top sahibini, takım tarafını, yeniden başlama durumunu ve sayaçları yönetir. Model 2, 90 adet bir dakikalık karar adımı kullanır. Pas veya şut uçuşu aynı adım içinde başlar ve çözülür. Eski modelin beş dakikası yalnız rapor toplama aralığı olarak model 2'de kalır.

Diziliş, takım hattı, yaklaşım, tempo ve genişlik hedef konumu değiştirir. Rakibe en yakın uygun savunmacı topa yaklaşır. Hız ve enerji hızı sınırlar. Kaleci topa göre kale önü yanal yerleşimini korur. İlk kalibrasyonda kaleci .519 saha derinliğine kadar gidebildi. Top sürme sınırı eklendikten sonra eşleşmeli örneklemde üst sınır .180 oldu. Canvas çakışma açması simülasyona geri yazılmaz.

Santra, taç, korner, serbest vuruş, penaltı ve kale vuruşu durumları var. Duran toplarda özel duvar, pozisyon işaretçisi, faul/VAR kararı ve ofsayt yok. Top ve oyuncu yerleşimi ilan edilmiş duran top başlangıcında kurulabilir. Açık oyunda topun sahibi varsa koordinat aynı oyuncunundur.
