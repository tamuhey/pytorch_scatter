from torch.autograd import Function

from .utils.ffi import get_func
from .utils.gen import gen


class ScatterMul(Function):
    @staticmethod
    def forward(ctx, out, src, index, dim):
        func = get_func('scatter_mul', src)
        func(dim, out, index, src)

        ctx.dim = dim
        ctx.mark_dirty(out)
        ctx.save_for_backward(out, src, index)

        return out

    @staticmethod
    def backward(ctx, grad_out):
        out, src, index = ctx.saved_variables

        grad_src = None
        if ctx.needs_input_grad[1]:
            grad_src = (grad_out * out)[index] / src

        return None, grad_src, None, None


def scatter_mul(src, index, dim=-1, out=None, dim_size=None, fill_value=1):
    r"""
    |

    .. image:: https://raw.githubusercontent.com/rusty1s/pytorch_scatter/
            master/docs/source/_figures/mul.svg?sanitize=true
        :align: center
        :width: 400px

    |

    Multiplies all values from the :attr:`src` tensor into :attr:`out` at the
    indices specified in the :attr:`index` tensor along an given axis
    :attr:`dim`.If multiple indices reference the same location, their
    **contributions multiply** (`cf.` :meth:`~torch_scatter.scatter_add`).

    For one-dimensional tensors, the operation computes

    .. math::
        \mathrm{out}_i = \mathrm{out}_i \cdot \prod_j \mathrm{src}_j

    where sum is over :math:`j` such that :math:`\mathrm{index}_j = i`.

    Args:
        src (Tensor): The source tensor.
        index (LongTensor): The indices of elements to scatter.
        dim (int, optional): The axis along which to index.
            (default: :obj:`-1`)
        out (Tensor, optional): The destination tensor. (default: :obj:`None`)
        dim_size (int, optional): If :attr:`out` is not given, automatically
            create output with size :attr:`dim_size` at dimension :attr:`dim`.
            If :attr:`dim_size` is not given, a minimal sized output tensor is
            returned. (default: :obj:`None`)
        fill_value (int, optional): If :attr:`out` is not given, automatically
            fill output tensor with :attr:`fill_value`. (default: :obj:`0`)

    :rtype: :class:`Tensor`

    .. testsetup::

        import torch

    .. testcode::

        from torch_scatter import scatter_mean
        src = torch.tensor([[2, 0, 1, 4, 3], [0, 2, 1, 3, 4]])
        index = torch.tensor([[4, 5, 4, 2, 3], [0, 0, 2, 2, 1]])
        out = src.new_zeros((2, 6))
        out = scatter_mean(src, index, out=out)
        print(out)

    .. testoutput::

        0.0000  0.0000  4.0000  3.0000  1.5000  0.0000
        1.0000  4.0000  2.0000  0.0000  0.0000  0.0000
       [torch.FloatTensor of size 2x6]
    """
    src, out, index, dim = gen(src, index, dim, out, dim_size, fill_value)
    return ScatterMul.apply(out, src, index, dim)
