Profile Loader for Jcard-based SIM/eSIM
====================================================

A sim profile loader program that can be used to read/write all fields/parameters
on Jcard-based programmable SIM/eSIM [eSIM-Applet]. 

This project can be used to test your own cellular network with customized profile and
multi-carrier functions.

## Usage

### Javacard reader
The reader is needed for [eSIM-Applet] and [eSIM-Loader] to let you install the 
eSIM applet on the Jcard and load profiles into it.
![reader](./docs/reader.jpeg)

### Install Dependencies 
- For Linux, you may need to install dependencies:
```$xslt
 sudo apt-get install pcscd pcsc-tools libccid libpcsclite-dev python-pyscard
```

- Install the required package by:

```$xslt
 pip2 install pyscard pytlv
```

### Enable eSIM functions for the Javacard

`./build-esim.py` is used to build eSIM structure on the Jcard (For eSIM multi-profile). It will build the SIM structures
for all the 3 slots in the [eSIM-Applet], and install one default profile:

```
 python2 ./build-esim.py
```

The dafault IMSI, OPC and KEY can be configured in the `build-esim.py`:

```$xslt
    IMSI = sr.imsi("001010000024038")
    OPC = "0102030405060708090A0B0C0D0E0F00"
    KEY = "0102030405060708090A0B0C0D0E0F00"
```
All default values of other fields can be configured in the folder `esim` by replacing the
data in the corresponding .txt files. For example, if you want to change `EF_LI(6F05)` in ADF, 
you can replace the Data field in the `esim/adf.txt`:
```$xslt
Name: 6F05 //EF_LI
 Type: transparent 
 FCI: 62258202412183026f05a50cc001009b043f002f05ca01808a01058b036f06028002000a880110 
 Data: ffffffffffffffffffff //Replace the fefault 'ff..ff' with your value
```


### Enable a single-profile SIM (Optional)
If the storage of the Javacard is limited or only a single profile is needed (like a normal SIM), 
you can install a single profile by:
```
 python2 ./profile-write.py
```
IMSI, OPC and KEY can be configured in the `profile-write.py` as before. 
All default values of other fields can be configured in the folder `profile` by replacing the
data in the corresponding .txt files as before.

### Read the current profile from Javacard (Optional)

After installing the profile, profile-read can extract current EF fields from Javacard SIM. 
By default, the profile will be exported to `./profile-read`:
```
 python2 ./profile-read.py
```



[eSIM-WING]: https://github.com/JinghaoZhao/eSIM-WING
[eSIM-Loader]: https://github.com/JinghaoZhao/eSIM-Loader
[eSIM-Applet]: https://github.com/JinghaoZhao/eSIM-Applet
[WING-SMDP]: https://github.com/JinghaoZhao/WING-SMDP
[LPA-App]: https://github.com/JinghaoZhao/LPA-App