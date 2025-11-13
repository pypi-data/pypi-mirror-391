
# amberNPS-api


amperNPS-api is a convenient python API to make predictions lethal blood concentrations (LBC) of new psychoactive substances (NPS). 

[amberNPS](https://ambernps.streamlit.app/) is a streamlit application developed by Tarcisio Nascimento Correa. For further details please the publication at [A QSAR-based application for the prediction of lethal blood concentration of new psychoactive substances](https://www.sciencedirect.com/science/article/pii/S2667118224000151)

## Installation

Install the latest version of amberNPS with pip:

```shell
pip install amberNPS
```

## Example usage

Import the amberNPS class, instatiate it then call the predict method with the SMILES string:
```pycon
>>> from amberNPS import amberNPS
>>> a = amberNPS()
>>> a = a.predict("Brc1cc2C(=NCc3nnc(C)n3c2cc1)c4ccccc4") # bromazolam
>>> preds
{'Drug Class': 'Benzodiazepines', 'LOLBC': 28.988149644904777,'LBC50': 151.32238377755087, 'HOLBC': 870.7153200659999}

```
Results are also stored as properties:

```pycon
>>> a.LOLBC
28.988149644904777
>>> a.LBC50
151.32238377755087
>>> a.HOLBC
870.7153200659999
>>> a.drug_class
'Benzodiazepines'
>>> a.smiles
'Brc1cc2C(=NCc3nnc(C)n3c2cc1)c4ccccc4'
```
The raw predictions (log10 of concentrations above) can also be accessed.

As a list:
```pycon
>>> a.lbc_preds
[1.0843620906924618, 0.36667941118940295, -0.3932936005597203]
```
Or using properties:
```pycon
>>> a.pLOLBC
1.0843620906924618
>>> a.pLBC50
0.36667941118940295
>>> a.pHOLBC
0.3932936005597203
```

You can also render the image of the structure (this may or may not work depending on IDE):
```pycon
a.structure
```
![example structure](assets/example.png)

## Documentation

The API reference is available at <https://ambernps-api.readthedocs.io/en/latest/amberNPS.html#module-amberNPS>.

## Contributing

- Feature ideas and bug reports are welcome on the [Issue Tracker](https://github.com/dpasin/amberNPS/issues).
- Fork the [source code](https://github.com/dpasin/amberNPS) on GitHub, make changes and file a pull request.

## License

PubChemPy is licensed under the [MIT license](https://github.com/dpasin/amberNPS/LICENSE).


