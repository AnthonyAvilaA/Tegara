import torch
import torch.nn as nn
import numpy as np
import torch.optim as optim

class SmallClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.criterion = nn.CrossEntropyLoss()
        self.net = nn.Sequential(
            nn.Linear(63, 128),
            nn.ReLU(),
            nn.Linear(128, 96),
            nn.ReLU(),
            nn.Linear(96, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 7),
        )
    
    def forward(self, x) -> torch.Tensor:
        return self.net(x)
    
    def normalize_sample(self, sample) -> np.ndarray | None:
        if len(sample) == 0:
            return None
        sample = np.array(sample, dtype=np.float32)  # <<-- CONVERSIÓN IMPORTANTE
        sample = sample - sample[0]                  # mover al origen
        max_val = np.max(np.abs(sample))
        if max_val == 0:
            return sample
        sample = sample / max_val                   # escalar
        return sample

    def fit(self, X, y, epochs=200) -> None:
        optimizer = optim.Adam(self.parameters(), lr=0.001)
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = self(X)
            loss = self.criterion(outputs, y)
            loss.backward()
            optimizer.step()
            if epoch % 50 == 0:
                print(epoch, loss.item())

    def predict(self, sample) -> tuple[float, int]:
        sample_norm = self.normalize_sample(sample)
        if sample_norm is None:
            return 0
        sample_flat = sample_norm.flatten().astype(np.float32)
        sample_tensor = torch.tensor(sample_flat).unsqueeze(0)
        
        self.eval()

        with torch.no_grad():
            outputs = self(sample_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            prob, predicted_class = torch.max(probabilities, 1)
        
        return prob.item(), predicted_class.item()