from regnet_module import Stem, Stage, Head

import torch
import torch.nn as nn


class AnyNetX(nn.Module):
    """
    Initial AnyNet design space.

    Consists of a simple stem, followed by the network body that performs the
    bulk of the computation, and a final network head that predicts the classes.
    """
    def __init__(self, num_blocks, block_widths, bottleneck_ratios, group_widths, stride, se_ratio, num_classes):
        super(AnyNetX, self).__init__()
        prev_conv_width = 32
        # Check the input parameters are valid
        for block_width, bottleneck_ratio, group_width in zip(block_widths, bottleneck_ratios, group_widths):
            assert block_width % (bottleneck_ratio * group_width) == 0
        # Construct the stem
        self.stem = Stem(prev_conv_width)
        # Construct the body
        self.body = nn.Sequential()
        for index, (block_width, num_block, bottleneck_ratio, group_width) in enumerate(zip(block_widths, num_blocks, bottleneck_ratios, group_widths)):
            stage = Stage(prev_conv_width, block_width, num_block, stride, bottleneck_ratio, group_width, se_ratio)
            self.body.add_module(f"Stage_{index}", stage)
            prev_conv_width = block_width
        # Construct the head
        self.head = Head(prev_conv_width, num_classes)

    def forward(self, x):
        x = self.stem(x)
        x = self.body(x)
        x = self.head(x)
        return x


class AnyNetXb(AnyNetX):
    def __init__(self, num_blocks, block_widths, bottleneck_ratios, group_widths, stride, se_ratio, num_classes):
        super(AnyNetXb, self).__init__(num_blocks, block_widths, bottleneck_ratios, group_widths, stride, se_ratio, num_classes)
        assert len(set(bottleneck_ratios)) == 1, "All bottleneck ratios must be equal"


class AnyNetXc(AnyNetXb):
    def __init__(self, num_blocks, block_widths, bottleneck_ratios, group_widths, stride, se_ratio, num_classes):
        super(AnyNetXc, self).__init__(num_blocks, block_widths, bottleneck_ratios, group_widths, stride, se_ratio, num_classes)
        assert len(set(group_widths)) == 1, "All group widths must be equal"


class AnyNetXd(AnyNetXc):
    def __init__(self, num_blocks, block_widths, bottleneck_ratios, group_widths, stride, se_ratio, num_classes):
        super(AnyNetXd, self).__init__(num_blocks, block_widths, bottleneck_ratios, group_widths, stride, se_ratio, num_classes)
        assert all(prev <= behind for prev, behind in zip(block_widths, block_widths[1:])), "Block widths must be monotonically increasing"


class AnyNetXe(AnyNetXd):
    def __init__(self, num_blocks, block_widths, bottleneck_ratios, group_widths, stride, se_ratio, num_classes):
        super(AnyNetXe, self).__init__(num_blocks, block_widths, bottleneck_ratios, group_widths, stride, se_ratio, num_classes)
        assert all(prev <= behind for prev, behind in zip(num_blocks[: -2], num_blocks[1:-1])), "Number of blocks must be monotonically increasing"


if __name__ == '__main__':
    num_blocks = [1, 2, 7, 12]
    block_widths = [32, 64, 160, 384]
    bottleneck_ratios = [1, 1, 1, 1]
    group_widths = [2, 2, 2, 2]
    model = AnyNetXe(num_blocks, block_widths, bottleneck_ratios,
        group_widths, stride = 1, se_ratio = 4, num_classes = 10)
    print(model)
    img = torch.randn(1, 3, 224, 224)
    print(model(img).shape)
    print(sum(p.numel() for p in model.parameters()))