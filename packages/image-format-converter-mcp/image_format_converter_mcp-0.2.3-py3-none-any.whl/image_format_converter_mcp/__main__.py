"""Main Entry Point for the Image Format Converter MCP Server."""

from .general_conversion import auto_convert_image, auto_convert_folder
from .gif_conversion import convert_images_to_gif
from .pdf_conversion import convert_images_to_pdf

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ErrorData
from mcp import McpError  # Import McpError for proper error handling
import gc
import sys
from typing import Union, Dict, Any, Optional

mcp = FastMCP("image-format-converter-mcp")


def ok(msg: str) -> Union[TextContent, list]:
    """Create a Success Response."""
    # FastMCP expects either TextContent or list of content items
    # When returning success, we should NOT set any error flags
    return TextContent(type="text", text=msg)


def error(msg: str, data: Any = None) -> None:
    """Raise an Error - FastMCP will handle the error propagation."""
    # Use McpError for proper error handling
    raise McpError(ErrorData(code=-1, message=msg, data=data))


def isError(result: Any) -> bool:
    """Check if a result represents an error condition.
    
    Args:
        result: The result to check (could be exception, error message, None, etc.)
    
    Returns:
        bool: True if result represents an error, False otherwise
    """
    if result is None:
        return True
    
    if isinstance(result, Exception):
        return True
    
    if isinstance(result, str):
        error_indicators = ['error', 'failed', 'exception', 'invalid', 'not found', 'cannot']
        return any(indicator in result.lower() for indicator in error_indicators)
    
    if isinstance(result, dict) and 'error' in result:
        return True
        
    return False


@mcp.tool("auto_convert_image", description="将单个或多个图片转换为指定格式(jpeg, png, webp, heic, avif, bmp, tiff, ico)并保存到输出目录。支持SVG输入格式(使用PyMuPDF，无需系统依赖)。参数: file_name (str 或 list) = 输入图片文件路径，支持单个文件路径或文件路径列表 || target_format (str) = 目标格式(jpeg, png, webp, heic, avif, bmp, tiff, ico) || output_dir (str) = 转换后文件保存的输出目录路径 || ico_sizes (list)(可选) = ICO图标尺寸列表，仅用于ico格式，例如[16,32,48,64,128,256]。默认使用原图尺寸，或者如果原图尺寸不是正方形则使用标准ICO尺寸 || dpi (int)(可选) = SVG转换时的DPI，默认300 || svg_backend (str)(可选) = SVG渲染后端(默认'auto'，使用PyMuPDF)")
def auto_convert_image_tool(file_name, target_format: str, output_dir: str, ico_sizes: Optional[list] = None, dpi: int = 300, svg_backend: str = "auto") -> TextContent:
    """Convert Single or Multiple Images to Target Format."""
    try:
        # First validate inputs before capturing output
        from pathlib import Path

        # Handle both single file and list of files for validation
        if isinstance(file_name, str):
            file_paths = [file_name]
        else:
            file_paths = file_name

        # Validate all input files
        for file_path in file_paths:
            input_path = Path(file_path)
            if not input_path.exists():
                raise McpError(ErrorData(
                    code=-1,
                    message=f"Failed to Convert Image: Input file does not exist: {file_path}",
                    data={"file_name": file_name, "target_format": target_format}
                ))
            if not input_path.is_file():
                raise McpError(ErrorData(
                    code=-1,
                    message=f"Failed to Convert Image: Input path is not a file: {file_path}",
                    data={"file_name": file_name, "target_format": target_format}
                ))

        # Capture stdout/stderr to Collect Warnings
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr

        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
            # 准备kwargs参数
            kwargs = {}
            if ico_sizes is not None:
                kwargs['ico_sizes'] = tuple(ico_sizes)
            if dpi is not None:
                kwargs['dpi'] = dpi
            if svg_backend is not None:
                kwargs['svg_backend'] = svg_backend
            result = auto_convert_image(file_name, target_format, output_dir, **kwargs)

        # Check if There Were Warnings
        output_text = output_buffer.getvalue()
        warnings = []
        if "(WARNING)" in output_text:
            warnings = [line.strip() for line in output_text.split('\n') if "(WARNING)" in line]

        if warnings:
            return ok(f"Successfully converted image(s) to: {result}\n\n(WARNING) Warnings:\n" + "\n".join(warnings))
        else:
            return ok(f"Successfully converted image(s) to: {result}")

    except McpError:
        # Re-raise McpError as is
        raise
    except Exception as e:
        # Convert any other exception to McpError
        error_msg = f"Failed to Convert Image: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)  # Debug logging
        raise McpError(ErrorData(
            code=-1,
            message=error_msg,
            data={"file_name": file_name, "target_format": target_format}
        ))
    finally:
        # Simple Memory Cleanup
        gc.collect()


@mcp.tool("auto_convert_images", description="批量转换图片文件列表为指定格式(jpeg, png, webp, heic, avif, bmp, tiff, ico)。支持SVG输入格式(使用PyMuPDF，无需系统依赖)。转换后的图片将保存在第一个文件所在目录的新子文件夹中。参数: input_files (list) = 图片文件路径列表 || target_format (str) = 目标格式(jpeg, png, webp, heic, avif, bmp, tiff, ico) || ico_sizes (list)(可选) = ICO图标尺寸列表，仅用于ico格式，例如[16,32,48,64,128,256]。默认使用智能尺寸选择 || dpi (int)(可选) = SVG转换时的DPI，默认300 || svg_backend (str)(可选) = SVG渲染后端(默认'auto'，使用PyMuPDF)")
def auto_convert_images_tool(input_files: list, target_format: str, ico_sizes: Optional[list] = None, dpi: int = 300, svg_backend: str = "auto") -> TextContent:
    """Batch Convert Multiple Image Files to Target Format."""
    try:
        # Validate input_files is a list
        if not input_files or not isinstance(input_files, list):
            raise McpError(ErrorData(
                code=-1,
                message="Failed to Convert Images: input_files must be a non-empty list of file paths",
                data={"input_files": input_files, "target_format": target_format}
            ))
        
        # Capture stdout/stderr to collect output
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
            # 准备kwargs参数
            kwargs = {}
            if ico_sizes is not None:
                kwargs['ico_sizes'] = tuple(ico_sizes)
            if dpi is not None:
                kwargs['dpi'] = dpi
            if svg_backend is not None:
                kwargs['svg_backend'] = svg_backend
            result = auto_convert_folder(input_files, target_format, **kwargs)
        
        # Get output text
        output_text = output_buffer.getvalue()
        
        # Check for failures and include error details
        if result.get('failed'):
            # Extract error messages from output
            error_lines = [line for line in output_text.split('\n') if 'WARNING' in line or 'ERROR' in line or 'Failed' in line]
            error_details = '\n'.join(error_lines) if error_lines else 'Unknown error'
            # Raise MCP error so caller sees isError=true when any file fails
            raise McpError(ErrorData(
                code=-1,
                message="Failed to Convert Some Images",
                data={
                    "converted": result.get("converted", []),
                    "failed": result.get("failed", []),
                    "skipped_already_target": result.get("skipped_already_target", []),
                    "output_folder": result.get("output_folder", "N/A"),
                    "details": error_details
                }
            ))
        
        return ok(f"Successfully converted {len(result.get('converted', []))} images.\nOutput folder: {result.get('output_folder', 'N/A')}")
        
    except McpError:
        # Re-raise McpError as is
        raise
    except Exception as e:
        # Convert any other exception to McpError
        raise McpError(ErrorData(
            code=-1,
            message=f"Failed to Convert Images: {str(e)}",
            data={"input_files": input_files, "target_format": target_format}
        ))
    finally:
        # Simple Memory Cleanup
        gc.collect()


@mcp.tool("convert_images_to_gif", description="将指定的图片文件列表(jpeg, png, webp, heic, avif, bmp, tiff, ico)合并创建GIF动画，并保存到指定输出目录，如未指定则保存到第一个文件所在目录。参数: input_files (list) = 图片文件路径列表 || output_dir (str)(可选) = 输出目录路径(不含文件名)，默认为第一个文件所在目录 || file_name (str)(可选) = 自定义文件名，默认自动命名 || duration (int)(可选) = 每帧持续时间(毫秒，接受1-10000ms)，默认100 || loop (int)(可选) = 播放循环次数(0=无限循环)，默认0 || color_mode (str)(可选) = 颜色模式'RGB'(全彩色)、'P'(索引色)或'L'(灰度)，默认'RGB' || color_count (int)(可选) = 颜色数量(接受2-256)，用于'P'和'L'模式('RGB'忽略)，默认256 || brightness (float)(可选) = 亮度0.0(最暗)到5.0(最亮)，默认1.0 || contrast (float)(可选) = 对比度0.0(最低)到5.0(最高)，默认1.0 || saturation (float)(可选) = 饱和度0.0(最低)到5.0(最高)，默认1.0 || ping_pong (bool)(可选) = 乒乓球播放模式(正向→反向→正向)，默认False || easing (str)(可选) = 缓动曲线'none'、'ease-in'、'ease-out'和'ease-in-out'，默认'none' || easing_strength (float)(可选) = 缓动强度0.1(轻微)到5.0(强烈)，默认1.0 || size_strategy (str)(可选) = 尺寸统一策略'auto'(保持原始)、'min_size'(使用最小)、'max_size'(使用最大)、'custom'(指定尺寸)，默认'auto' || resize_mode (str)(可选) = 调整大小行为'fit'(保持宽高比加填充)、'fill'(裁剪填充)、'stretch'(拉伸适应)，默认'fit' || alignment (str)(可选) = fit/fill模式的位置'center'、'top_left'、'top_right'、'bottom_left'、'bottom_right'，默认'center' || target_width (int)(可选) = 自定义尺寸策略的宽度 || target_height (int)(可选) = 自定义尺寸策略的高度 || background_color (str)(可选) = fit模式的背景色(CSS颜色名或十六进制)，默认'black'")
def convert_images_to_gif_tool(
    input_files: list,
    file_name: str = None,
    output_dir: str = None,
    duration: int = 100,
    loop: int = 0,
    color_mode: str = "RGB",
    color_count: int = 256,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    ping_pong: bool = False,
    easing: str = "none",
    easing_strength: float = 1.0,
    size_strategy: str = "auto",
    resize_mode: str = "fit",
    alignment: str = "center", 
    target_width: int = None,
    target_height: int = None,
    background_color: str = "black"
) -> TextContent:
    """Convert Multiple Images to Animated GIF."""
    try:
        # First validate inputs before processing
        if not input_files or not isinstance(input_files, list):
            raise McpError(ErrorData(
                code=-1,
                message="Failed to Create GIF: input_files must be a non-empty list of file paths",
                data={"input_files": input_files, "duration": duration, "color_mode": color_mode}
            ))
        
        # Capture stdout/stderr to Collect Warnings
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
            result = convert_images_to_gif(
                input_files, file_name, output_dir, duration, loop, color_mode, color_count,
                brightness, contrast, saturation, ping_pong, easing, easing_strength,
                size_strategy, resize_mode, alignment, target_width, target_height, background_color
            )
        
        # Check if There Were Warnings
        output_text = output_buffer.getvalue()
        warnings = []
        if "(WARNING)" in output_text:
            warnings = [line.strip() for line in output_text.split('\n') if "(WARNING)" in line]
        
        if warnings:
            return ok(f"Successfully created GIF: {result}\n\n(WARNING) Warnings:\n" + "\n".join(warnings))
        else:
            return ok(f"Successfully created GIF: {result}")
            
    except McpError:
        # Re-raise McpError as is
        raise
    except Exception as e:
        # Convert any other exception to McpError  
        raise McpError(ErrorData(
            code=-1,
            message=f"Failed to Create GIF: {str(e)}",
            data={
                "input_files": input_files,
                "duration": duration,
                "color_mode": color_mode
            }
        ))
    finally:
        # Simple Memory Cleanup
        gc.collect()


@mcp.tool("convert_images_to_pdf", description="将指定的图片文件列表(jpeg, png, webp, heic, avif, bmp, tiff, ico)合并创建PDF文档，每张图片占一页，并保存到指定输出目录，如未指定则保存到第一个文件所在目录。参数: input_files (list) = 图片文件路径列表 || output_dir (str)(可选) = 输出目录路径(不含文件名)，默认为第一个文件所在目录 || file_name (str)(可选) = 自定义文件名，默认自动命名 || sort_order (str)(可选) = 图片文件合并(页面)顺序'alphabetical'(字母数字a-z&0-9)、'creation_time'(创建时间最新-最早)、'modification_time'(修改时间最新-最早)，默认'alphabetical' || page_size (str)(可选) = PDF页面尺寸A3/A4/A5/B3/B4/B5/Letter/Legal/Executive/Tabloid/16:9/4:3/Square，默认'A4' || dpi (int)(可选) = PDF分辨率(接受72-1200)，默认300 || fit_to_page (bool)(可选) = 缩放图片以完全适应PDF页面，默认True || center_image (bool)(可选) = 居中显示图片，默认True || background_color (str)(可选) = 背景色'white'、'light gray'、'gray'、'dark gray'、'black'、'light red'、'red'、'dark red'、'yellow'、'orange'、'lime'、'light green'、'green'、'dark green'、'light blue'、'blue'、'dark blue'、'light purple'、'purple'、'dark purple'、'light pink'、'pink'、'dark pink'、'light brown'、'brown'、'dark brown'，默认'white'")
def convert_images_to_pdf_tool(
    input_files: list,
    output_dir: str = None,
    file_name: str = None,
    sort_order: str = "alphabetical",
    page_size: str = "A4",
    dpi: int = 300,
    fit_to_page: bool = True,
    center_image: bool = True,
    background_color: str = "white"
) -> TextContent:
    """Combine Multiple Images into PDF."""
    try:
        # First validate inputs before processing
        if not input_files or not isinstance(input_files, list):
            raise McpError(ErrorData(
                code=-1,
                message="Failed to Create PDF: input_files must be a non-empty list of file paths",
                data={"input_files": input_files, "page_size": page_size, "dpi": dpi}
            ))
        
        # Capture stdout/stderr to Collect Warnings
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
            result = convert_images_to_pdf(
                input_files, output_dir, file_name, sort_order, page_size,
                dpi, fit_to_page, center_image, background_color
            )
        
        # Check if There Were Warnings
        output_text = output_buffer.getvalue()
        warnings = []
        if "(WARNING)" in output_text:
            warnings = [line.strip() for line in output_text.split('\n') if "(WARNING)" in line]
        
        if warnings:
            return ok(f"Successfully created PDF: {result}\n\n(WARNING) Warnings:\n" + "\n".join(warnings))
        else:
            return ok(f"Successfully created PDF: {result}")
            
    except McpError:
        # Re-raise McpError as is
        raise
    except Exception as e:
        # Convert any other exception to McpError
        raise McpError(ErrorData(
            code=-1,
            message=f"Failed to Create PDF: {str(e)}",
            data={
                "input_files": input_files,
                "page_size": page_size,
                "dpi": dpi
            }
        ))
    finally:
        # Simple Memory Cleanup
        gc.collect()


def main():
    """Run the MCP Server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
