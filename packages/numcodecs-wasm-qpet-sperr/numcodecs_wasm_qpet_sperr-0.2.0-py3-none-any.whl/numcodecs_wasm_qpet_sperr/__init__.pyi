__all__ = ['QpetSperr']

import numcodecs.abc

class QpetSperr(numcodecs.abc.Codec):
    r"""
    Codec providing compression using QPET-SPERR.
    
    Arrays that are higher-dimensional than 3D are encoded by compressing each
    3D slice with QPET-SPERR independently. Specifically, the array's shape is
    interpreted as `[.., depth, height, width]`. If you want to compress 3D
    slices along three different axes, you can swizzle the array axes
    beforehand.
    
    Parameters
    ----------
    mode : ...
         - "qoi-symbolic": Symbolic Quantity of Interest
    qoi : ...
        quantity of interest expression
    qoi_pwe : ...
        positive (pointwise) absolute error bound over the quantity of
        interest
    _version : ..., optional, default = "0.2.0"
        The codec's encoding format version. Do not provide this parameter explicitly.
    data_pwe : ..., optional, default = None
        optional positive pointwise absolute error bound over the data
    high_prec : ..., optional, default = False
        high precision mode for SPERR, useful for small error bounds
    qoi_block_size : ..., optional, default = [1,1,1]
        3D block size (z,y,x) over which the quantity of interest errors
        are averaged, 1x1x1 for pointwise
    qoi_k : ..., optional, default = 3.0
        positive quantity of interest k parameter (3.0 is a good default)
    sperr_chunks : ..., optional, default = [256,256,256]
        3D size of the chunks (z,y,x) that SPERR uses internally
    """

    def __init__(self, mode, qoi, qoi_pwe, _version='0.2.0', data_pwe=None, high_prec=False, qoi_block_size=[1, 1, 1], qoi_k=3.0, sperr_chunks=[256, 256, 256]): ...

    codec_id = 'qpet-sperr.rs'

    def decode(self, buf, out=None):
        r"""
        Decode the data in `buf`.
        
        Parameters
        ----------
        buf : Buffer
            Encoded data. May be any object supporting the new-style buffer
            protocol.
        out : Buffer, optional
            Writeable buffer to store decoded data. N.B. if provided, this buffer must
            be exactly the right size to store the decoded data.
        
        Returns
        -------
        dec : Buffer
            Decoded data. May be any object supporting the new-style
            buffer protocol.
        """
        ...

    def encode(self, buf):
        r"""
        Encode the data in `buf`.
        
        Parameters
        ----------
        buf : Buffer
            Data to be encoded. May be any object supporting the new-style
            buffer protocol.
        
        Returns
        -------
        enc : Buffer
            Encoded data. May be any object supporting the new-style buffer
            protocol.
        """
        ...

    @classmethod
    def from_config(cls, config):
        r"""
        Instantiate the codec from a configuration [`dict`][dict].
        
        Parameters
        ----------
        config : dict
            Configuration of the codec.
        
        Returns
        -------
        codec : Self
            Instantiated codec.
        """
        ...

    def get_config(self):
        r"""
        Returns the configuration of the codec.
        
        [`numcodecs.registry.get_codec(config)`][numcodecs.registry.get_codec]
        can be used to reconstruct this codec from the returned config.
        
        Returns
        -------
        config : dict
            Configuration of the codec.
        """
        ...
