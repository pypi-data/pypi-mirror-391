import torch
import torch.nn.functional as F
from torch import nn

backwarp_grid_cache = {}

def warp(
    input_tensor: torch.Tensor,
    flow_tensor: torch.Tensor,
    device: torch.device
) -> torch.Tensor:
    """
    Warp the input tensor using the flow tensor.
    The flow tensor is expected to be in the format of (batch_size, 2, height,
    width), where the first channel represents the horizontal flow and the
    second channel represents the vertical flow.
    The input tensor is expected to be in the format of (batch_size, channels,
    height, width).

    Parameters
    ----------
    input_tensor : torch.Tensor
        The input tensor to be warped.
    flow_tensor : torch.Tensor
        The flow tensor used for warping.
    device : torch.device
        The device on which the tensors are located.

    Returns
    -------
    torch.Tensor
        The warped tensor.

    """
    key = (str(flow_tensor.device), str(flow_tensor.size()))

    if key not in backwarp_grid_cache:
        horizontal = torch.linspace(
            -1.0, 1.0, flow_tensor.shape[3], device=device
        ).view(
            1, 1, 1, flow_tensor.shape[3]
        ).expand(flow_tensor.shape[0], -1, flow_tensor.shape[2], -1)

        vertical = torch.linspace(
            -1.0, 1.0, flow_tensor.shape[2], device=device
        ).view(
            1, 1, flow_tensor.shape[2], 1
        ).expand(flow_tensor.shape[0], -1, -1, flow_tensor.shape[3])

        backwarp_grid_cache[key] = torch.cat(
            [horizontal, vertical], dim=1
        ).to(device)

    normalized_flow = torch.cat([
        flow_tensor[:, 0:1, :, :] / ((input_tensor.shape[3] - 1.0) / 2.0),
        flow_tensor[:, 1:2, :, :] / ((input_tensor.shape[2] - 1.0) / 2.0)
    ], dim=1)

    sampling_grid = (
        backwarp_grid_cache[key] + normalized_flow
    ).permute(0, 2, 3, 1)

    return torch.nn.functional.grid_sample(
        input=input_tensor,
        grid=sampling_grid,
        mode="bilinear",
        padding_mode="border",
        align_corners=True
    )

def conv(
        in_channels: int,
        out_channels: int,
        kernel_size: int=3,
        stride: int=1,
        padding: int=1,
        dilation: int=1
) -> nn.Sequential:
    """
    Create a convolutional layer with LeakyReLU activation.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    kernel_size : int, optional
        Size of the convolutional kernel (default is 3).
    stride : int, optional
        Stride of the convolution (default is 1).
    padding : int, optional
        Padding added to all sides of the input (default is 1).
    dilation : int, optional
        Spacing between kernel elements (default is 1).

    Returns
    -------
    nn.Sequential
        A sequential model containing a convolutional layer and LeakyReLU activation.

    """
    return nn.Sequential(
        nn.Conv2d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            bias=True
        ),
        nn.LeakyReLU(0.2, inplace=True)
    )

def conv_bn(
        in_channels: int,
        out_channels: int,
        kernel_size: int=3,
        stride: int=1,
        padding: int=1,
        dilation: int=1
) -> nn.Sequential:
    """
    Create a convolutional layer with Batch Normalization and LeakyReLU activation.

    Parameters
    ----------
    in_channels : int
        Number of input channels.
    out_channels : int
        Number of output channels.
    kernel_size : int, optional
        Size of the convolutional kernel (default is 3).
    stride : int, optional
        Stride of the convolution (default is 1).
    padding : int, optional
        Padding added to all sides of the input (default is 1).
    dilation : int, optional
        Spacing between kernel elements (default is 1).

    Returns
    -------
    nn.Sequential
        A sequential model containing a convolutional layer, Batch Normalization,
        and LeakyReLU activation.

    """
    return nn.Sequential(
        nn.Conv2d(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            bias=False
        ),
        nn.BatchNorm2d(out_channels),
        nn.LeakyReLU(0.2, inplace=True)
    )

class Head(nn.Module):
    """
    Head module for the IFNet model.
    This module consists of several convolutional layers followed by LeakyReLU
    activation. It is used to process the input images and extract features.

    The output of the last convolutional layer is used as the input for the
    subsequent blocks in the IFNet model.

    Attributes
    ----------
    cnn0 : nn.Conv2d
        First convolutional layer.
    cnn1 : nn.Conv2d
        Second convolutional layer.
    cnn2 : nn.Conv2d
        Third convolutional layer.
    cnn3 : nn.ConvTranspose2d
        Fourth convolutional layer (transposed).
    relu : nn.LeakyReLU
        LeakyReLU activation function.

    """

    cnn0: nn.Conv2d
    cnn1: nn.Conv2d
    cnn2: nn.Conv2d
    cnn3: nn.ConvTranspose2d
    relu: nn.LeakyReLU

    def __init__(self) -> None:
        """
        Initialize the Head module.
        """
        super().__init__()
        self.cnn0 = nn.Conv2d(3, 16, 3, 2, 1)
        self.cnn1 = nn.Conv2d(16, 16, 3, 1, 1)
        self.cnn2 = nn.Conv2d(16, 16, 3, 1, 1)
        self.cnn3 = nn.ConvTranspose2d(16, 4, 4, 2, 1)
        self.relu = nn.LeakyReLU(0.2, inplace=True)

    def forward(self, x: torch.Tensor, feat: bool=False) -> torch.Tensor:
        """
        Forward pass through the Head module.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, channels, height, width).
        feat : bool, optional
            If True, return the intermediate features (default is False).

        Returns
        -------
        torch.Tensor
            Output tensor after passing through the Head module.
            If feat is True, return a list of intermediate features.

        """
        x0 = self.cnn0(x)
        x = self.relu(x0)

        x1 = self.cnn1(x)
        x = self.relu(x1)

        x2 = self.cnn2(x)
        x = self.relu(x2)
        x3 = self.cnn3(x)

        if feat:
            return [x0, x1, x2, x3]
        return x3

class ResConv(nn.Module):
    """
    Residual Convolutional Block.
    This module consists of a convolutional layer followed by a LeakyReLU
    activation. It also includes a learnable parameter beta that scales the
    output of the convolutional layer.

    The input is added to the output of the convolutional layer, creating a
    residual connection. This helps in training deep networks by allowing
    gradients to flow through the network more easily.

    Attributes
    ----------
    conv : nn.Conv2d
        Convolutional layer.
    beta : nn.Parameter
        Learnable parameter that scales the output of the convolutional layer.
    relu : nn.LeakyReLU
        LeakyReLU activation function.

    """

    conv: nn.Conv2d
    beta: nn.Parameter
    relu: nn.LeakyReLU

    def __init__(self, n_channels: int, dilation: int=1) -> None:
        """
        Initialize the ResConv module.

        Parameters
        ----------
        n_channels : int
            Number of channels in the input tensor.
        dilation : int, optional
            Dilation rate for the convolutional layer (default is 1).

        """
        super().__init__()
        self.conv = nn.Conv2d(
            n_channels, n_channels, 3, 1, dilation, dilation=dilation, groups=1
        )
        self.beta = nn.Parameter(
            torch.ones((1, n_channels, 1, 1)), requires_grad=True
        )
        self.relu = nn.LeakyReLU(0.2, inplace=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the ResConv module.
        Applies the convolutional layer, scales the output with beta,
        and adds the input to the output.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, channels, height, width).

        Returns
        -------
        torch.Tensor
            Output tensor after passing through the ResConv module.

        """
        return self.relu(self.conv(x) * self.beta + x)

class IFBlock(nn.Module):
    """
    Intermediate Flow Block.
    This module consists of several convolutional layers and residual blocks.
    It processes the input images and features, and outputs the flow and mask.

    Attributes
    ----------
    conv0 : nn.Sequential
        Initial convolutional layers for downsampling the input.
    conv_block : nn.Sequential
        Residual convolutional blocks for processing the features.
    last_conv : nn.Sequential
        Final convolutional layers for upsampling the output.

    """

    conv0: nn.Sequential
    convblock: nn.Sequential
    lastconv: nn.Sequential

    def __init__(self, in_channels :int, c :int=64) -> None:
        """
        Initialize the IFBlock module.

        Parameters
        ----------
        in_channels : int
            Number of input channels for the convolutional layers.
        c : int, optional
            Number of channels in the intermediate flow (default is 64).

        """
        super().__init__()

        self.conv0 = nn.Sequential(
            conv(in_channels, c//2, 3, 2, 1),
            conv(c//2, c, 3, 2, 1),
        )

        self.convblock = nn.Sequential(
            ResConv(c),
            ResConv(c),
            ResConv(c),
            ResConv(c),
            ResConv(c),
            ResConv(c),
            ResConv(c),
            ResConv(c),
        )
        self.lastconv = nn.Sequential(
            nn.ConvTranspose2d(c, 4*13, 4, 2, 1),
            nn.PixelShuffle(2)
        )

    def forward(
        self, x: torch.Tensor, flow: torch.Tensor=None, scale: int=1
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass through the IFBlock module.
        Applies the initial convolutional layers, residual blocks, and final
        convolutional layers to the input. The output includes the flow, mask,
        and features.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, channels, height, width).
        flow : torch.Tensor, optional
            Flow tensor of shape (batch_size, 4, height, width) (default is
            None). This tensor is used to warp the input images. Warping
            consists of applying the flow to the input images to create a new
            imaage, which is then used as input to the next block.
        scale : int, optional
            Scale factor for upsampling the output (default is 1).

        Returns
        -------
        tuple[torch.Tensor, torch.Tensor, torch.Tensor]
            A tuple containing the flow, mask, and features after passing through
            the IFBlock module.
            - flow: Tensor of shape (batch_size, 4, height, width).
            - mask: Tensor of shape (batch_size, 1, height, width).
            - feat: Tensor of shape (batch_size, channels, height, width).

        """
        x = F.interpolate(
            x, scale_factor= 1. / scale, mode="bilinear", align_corners=False
        )

        if flow is not None:
            flow = F.interpolate(
                flow, scale_factor= 1. / scale,
                mode="bilinear",
                align_corners=False
            ) * 1. / scale
            x = torch.cat((x, flow), 1)

        feat = self.conv0(x)
        feat = self.convblock(feat)

        tmp = self.lastconv(feat)
        tmp = F.interpolate(
            tmp, scale_factor=scale, mode="bilinear", align_corners=False
        )

        flow = tmp[:, :4] * scale
        mask = tmp[:, 4:5]
        feat = tmp[:, 5:]

        return flow, mask, feat

class IFNet(nn.Module):
    """
    Intermediate Flow Network (IFNet).
    This module consists of several IFBlock modules and a Head module.
    It processes the input images and features, and outputs the flow, mask,
    and merged images.

    Attributes
    ----------
    block0 : IFBlock
        First IFBlock module.
    block1 : IFBlock
        Second IFBlock module.
    block2 : IFBlock
        Third IFBlock module.
    block3 : IFBlock
        Fourth IFBlock module.
    block4 : IFBlock
        Fifth IFBlock module.
    encode : Head
        Head module for processing the input images.
    device : torch.device
        Device on which the model is running (CPU or GPU).

    """

    block0: IFBlock
    block1: IFBlock
    block2: IFBlock
    block3: IFBlock
    block4: IFBlock
    encode: Head
    device: torch.device

    def __init__(self, device: torch.device) -> None:
        """
        Initialize the IFNet module.
        """
        super().__init__()
        self.block0 = IFBlock(7+8, c=192)
        self.block1 = IFBlock(8+4+8+8, c=128)
        self.block2 = IFBlock(8+4+8+8, c=96)
        self.block3 = IFBlock(8+4+8+8, c=64)
        self.block4 = IFBlock(8+4+8+8, c=32)
        self.encode = Head()
        self.device = device

    def forward(
        self,
        x: torch.Tensor,
        timestep: int | torch.Tensor=0.5,
        scale_list: tuple[int]=(8, 4, 2, 1),
        ensemble: bool=False
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass through the IFNet module. Applies the IFBlock modules and
        Head module to the input images. The output includes the flow, mask,
        and merged images.

        - The flow is a tensor that represents the motion
        between the two input images.
        - The mask is a tensor that indicates the occlusion between the two
        images.
        - The merged images are the result of blending the two input images
        based on the flow and mask.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape (batch_size, channels, height, width).
        timestep : int | torch.Tensor, optional
            Timestep value for the model (default is 0.5). If a tensor is
            provided, it should have the same shape as the input tensor.
        scale_list : tuple[int], optional
            Scale factors for the IFBlock modules (default is (8, 4, 2, 1)).
        ensemble : bool, optional
            If True, use ensemble mode for the model (default is False). In
            ensemble mode, the model uses multiple passes to improve accuracy.

        Returns
        -------
        tuple[torch.Tensor, torch.Tensor, torch.Tensor]
            A tuple containing the flow, mask, and merged images after passing
            through the IFNet module.
            - flow: List of tensors representing the flow at each block.
            - mask: Tensor of shape (batch_size, 1, height, width).
            - merged: List of tuples containing the warped images at each
            block.

        """
        channel = x.shape[1] // 2
        img0 = x[:, :channel]
        img1 = x[:, channel:]

        if not torch.is_tensor(timestep):
            timestep = (x[:, :1].clone() * 0 + 1) * timestep
        else:
            timestep = timestep.repeat(1, 1, img0.shape[2], img0.shape[3])

        f0 = self.encode(img0[:, :3])
        f1 = self.encode(img1[:, :3])

        flow_list = []
        merged = []
        mask_list = []
        warped_img0 = img0
        warped_img1 = img1
        flow = None
        mask = None
        block = [self.block0, self.block1, self.block2, self.block3, self.block4]

        for i in range(5):
            if flow is None:
                flow, mask, feat = block[i](
                    torch.cat((img0[:, :3], img1[:, :3], f0, f1, timestep), 1),
                    None,
                    scale=scale_list[i]
                )
                if ensemble:
                    print("warning: ensemble is not supported since RIFEv4.21")
            else:
                wf0 = warp(f0, flow[:, :2], self.device)
                wf1 = warp(f1, flow[:, 2:4], self.device)
                fd, m0, feat = block[i](
                    torch.cat(
                        (
                            warped_img0[:, :3],
                            warped_img1[:, :3],
                            wf0,
                            wf1,
                            timestep,
                            mask,
                            feat
                        ),
                        1
                    ),
                    flow,
                    scale=scale_list[i]
                )

                if ensemble:
                    print("warning: ensemble is not supported since RIFEv4.21")
                else:
                    mask = m0

                flow = flow + fd

            mask_list.append(mask)
            flow_list.append(flow)
            warped_img0 = warp(img0, flow[:, :2], self.device)
            warped_img1 = warp(img1, flow[:, 2:4], self.device)
            merged.append((warped_img0, warped_img1))

        mask = torch.sigmoid(mask)
        merged[4] = (warped_img0 * mask + warped_img1 * (1 - mask))

        return flow_list, mask_list[4], merged
