# Cython interface to primecount (primecountpy fork)

This is a Cython interface to the C++ library [primecount](https://github.com/kimwalisch/primecount).

It is a compatible fork of [primecountpy](https://pypi.org/project/primecountpy/).


Quick installation and testing:

1) Install primecount C++ library
```
cd /tmp/
git clone https://github.com/kimwalisch/primecount
cd primecount
cmake . -DBUILD_SHARED_LIBS=ON
make -j
sudo make install
sudo ldconfig # linux only
```
2) in this repo, do
```
pip install . --user
```
3)

`python3`
and
```
>>> import primecountpy as primecount
>>> primecount.prime_pi(1000)
```

More details on installation without root (sudo) access,
and testing with `pytest`, may be found in the [manual](https://primecountpy.readthedocs.io).


## License

Distributed under the terms of the [GNU General Public
License](./LICENSE) (GPL) as published by the [Free Software
Foundation](https://www.fsf.org/); either version 2 of the License,
or (at your option) any later version.
