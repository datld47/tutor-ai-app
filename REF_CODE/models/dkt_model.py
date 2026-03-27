import torch
import torch.nn as nn

class DKT(nn.Module):
    def __init__(self, num_concepts, hidden_dim=64, layer_dim=1, output_dim=1):
        super(DKT, self).__init__()
        self.hidden_dim = hidden_dim
        self.layer_dim = layer_dim
        
        # Embedding: Chuyển đổi ID bài học thành vector
        # Input size = num_concepts * 2 (Vì mỗi concept có 2 trạng thái: Đúng hoặc Sai)
        self.embedding = nn.Embedding(num_concepts * 2, hidden_dim)
        
        # LSTM Layer: Bộ nhớ dài hạn
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, layer_dim, batch_first=True)
        
        # Fully Connected Layer: Đầu ra dự đoán
        self.fc = nn.Linear(hidden_dim, num_concepts)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (batch_size, sequence_length)
        embed = self.embedding(x) # -> (batch, seq, hidden)
        
        # LSTM forward
        out, (hn, cn) = self.lstm(embed)
        
        # Đưa qua lớp Linear để dự đoán xác suất cho TẤT CẢ các concept
        out = self.fc(out) 
        out = self.sigmoid(out)
        
        return out
