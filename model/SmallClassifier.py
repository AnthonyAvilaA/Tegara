import torch
import torch.nn as nn
import numpy as np
import torch.optim as optim

class SmallClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.criterion = nn.BCELoss()
        self.net = nn.Sequential(
            nn.Linear(63, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
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

    def predict(self, sample) -> int:
        sample = self.normalize_sample(sample).flatten().astype(np.float32)
        sample = torch.tensor(sample)
        prob = self(sample).item()
        return 1 if prob > 0.5 else 0