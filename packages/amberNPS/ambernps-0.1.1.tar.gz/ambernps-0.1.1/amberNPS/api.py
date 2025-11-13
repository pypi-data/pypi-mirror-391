import pickle
from pathlib import Path
from typing import Self

import numpy as np
import pandas as pd
from PIL import Image
from mordred import (Calculator, AdjacencyMatrix, Autocorrelation, EState, DistanceMatrix,
                     TopologicalIndex, BCUT, MoeType, RingCount, BaryszMatrix, ExtendedTopochemicalAtom,
                     TopologicalCharge)
from rdkit import Chem
from rdkit.Chem import Draw, MACCSkeys, rdMolDescriptors


class amberNPS:

    def __init__(self,
                 mlp: str = './amberNPS/models/multitask_regressor.pkl',
                 scaler: str = './amberNPS//models/scaler.pkl',
                 rf: str = './amberNPS/models/random_forest_model.pkl',
                 le: str = './amberNPS//models/label_encoder.pkl'
                 ):

        self.mlp = self._load_pickle(mlp)
        self.scaler = self._load_pickle(scaler)
        self.rf = self._load_pickle(rf)
        self.le = self._load_pickle(le)
        self.calc = self._register_descriptors(Calculator)
        self.drug_class = None
        self.LOLBC = None
        self.LBC50 = None
        self.HOLBC = None
        self.mol = None
        self.smiles = None
        self.lbc_preds = None
        self.mw = None

    @classmethod
    def convert_pLBC_to_LBC(cls, pLBC: float, mw: float) -> float:
        """Performs antilog transformation of the predicted LBC values"""
        LBCmol = 10 ** -pLBC
        LBC = LBCmol * mw
        return LBC
    
    @staticmethod
    def _load_pickle(file_path: str | Path) -> None:
        """
        Loads a pickle file safely, accepting string or Path-like objects.
        Raises:
            TypeError: if file_path is not str or Path
            FileNotFoundError: if the file does not exist
            pickle.UnpicklingError: if pickle fails to load
        """

        if not isinstance(file_path, (str, Path)):
            raise TypeError(f"Expected str or Path, got {type(file_path).__name__}")

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with path.open('rb') as f:
                return pickle.load(f)
        except pickle.UnpicklingError as e:
            raise ValueError(f"Failed to load pickle from {path}: {e}")

    @staticmethod
    def _register_descriptors(calculator) -> Calculator:
        """Register specific Mordred descriptors used for predictions."""
        c = calculator()
        c.register(AdjacencyMatrix.AdjacencyMatrix('VR1'))
        c.register(Autocorrelation.ATSC(0, 'p'))
        c.register(Autocorrelation.ATSC(2, 'i'))
        c.register(DistanceMatrix.DistanceMatrix('SpMax'))
        c.register(EState.AtomTypeEState('count', 'dCH2'))
        c.register(EState.AtomTypeEState('sum', 'aaaC'))
        c.register(MoeType.EState_VSA(2))
        c.register(RingCount.RingCount(11, False, True, True, None))
        c.register(Autocorrelation.ATS(5, 's'))
        c.register(Autocorrelation.ATSC(0, 'Z'))
        c.register(BCUT.BCUT('d', -1))
        c.register(BaryszMatrix.BaryszMatrix('are', 'SpDiam'))
        c.register(EState.AtomTypeEState('sum', 'dCH2'))
        c.register(ExtendedTopochemicalAtom.EtaVEMCount('ns_d', True))
        c.register(RingCount.RingCount(11, False, True, False, True))
        c.register(TopologicalCharge.TopologicalCharge('raw', 9))
        c.register(AdjacencyMatrix.AdjacencyMatrix('VR2'))
        c.register(Autocorrelation.ATSC(5, 's'))
        c.register(Autocorrelation.AATSC(1, 's'))
        c.register(Autocorrelation.GATS(7, 's'))
        c.register(BaryszMatrix.BaryszMatrix('are', 'SpMAD'))
        c.register(EState.AtomTypeEState('sum', 'dO'))
        c.register(MoeType.PEOE_VSA(13))
        c.register(MoeType.VSA_EState(8))
        c.register(RingCount.RingCount(5, True, False, False, None))
        c.register(TopologicalIndex.Diameter())
        c.register(TopologicalIndex.PetitjeanIndex())

        return c
    
    @property
    def structure(self) -> Image:
        """Generates image of structure in the console"""
        img = Draw.MolToImage(self.mol)
        return img
    
    def predict(self, smiles: str) -> Self:
        """
        Predicts the drug class and lethal blood concentrations (LBC)
        for the smiles and sets them as instance properties.

        """

        if not isinstance(smiles, str):
            raise TypeError(f"Expected str, got {type(smiles).__name__}")

        # Convert smiles to mol object
        self.smiles = smiles
        self.mol = Chem.MolFromSmiles(self.smiles)

        if not self.mol:
            raise ValueError(f'Could not parse smiles to mol object: {self.smiles}')

        # calculate exact molecular weight
        self.mw = rdMolDescriptors.CalcExactMolWt(self.mol)
            
        # Predict drug class and LBCs
        try:
            self.drug_class = self._predict_drug_class()
            self.lbc_preds = self._predict_lbc()
        except Exception as e:
            raise RuntimeError(f"Prediction failed for {smiles}: {e}")
        
        # Unpack predictions
        self.pLOLBC, self.pLBC50, self.pHOLBC = self.lbc_preds

        # Perform antilog transformation
        self.LOLBC = self.convert_pLBC_to_LBC(self.lbc_preds[0], self.mw)
        self.LBC50 = self.convert_pLBC_to_LBC(self.lbc_preds[1], self.mw)
        self.HOLBC = self.convert_pLBC_to_LBC(self.lbc_preds[2], self.mw)
        
        return self.to_dict()


    def to_dict(self) -> dict[str, float | str]:
        """
        Returns a dictionary containing predicted drug class and LBC values.

        """
        return {
            'Drug Class': self.drug_class,
            'LOLBC': self.LOLBC,
            'LBC50': self.LBC50,
            'HOLBC': self.HOLBC,
        }

    # -------------------
    # Private Members 
    # -------------------
    
    def _compute_maccs(self) -> pd.DataFrame:
        """
        Generates the MACCS keys for the compound used for predicting
        the compound's drug class.

        """
        maccs = MACCSkeys.GenMACCSKeys(self.mol)
        maccs_df = pd.DataFrame([list(maccs)[1:]], columns=[f"MACCS_{i}" for i in range(1, 167)])
        return maccs_df

    def _predict_lbc(self) -> list[float]:
        """
        Predicts the low, median and high LBC and return a list.
        i.e. [pLOLBC, pLBC50, pHOLBC]

        """
        features = self._compute_features()
        features = self.scaler.transform(features)
        pred = self.mlp.predict(features).flatten().tolist()
        return pred

    def _predict_drug_class(self) -> str:
        """Predicts drug class using trained random forest classifier"""

        maccs_keys = self._compute_maccs()
        drug_class = self.rf.predict(maccs_keys)
        drug_class = self.le.inverse_transform(drug_class)[0]
        return drug_class

    def _compute_features(self) -> np.ndarray:
        """Compute feature array for predictions using Mordred calculator"""

        features = np.array(self.calc(self.mol)).reshape(1, -1)
        return features



