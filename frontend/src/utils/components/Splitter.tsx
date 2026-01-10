import { useEffect, useState, ReactNode } from "react"
import { ResizableBox } from "react-resizable"
import { GrDrag } from "react-icons/gr"
import "react-resizable/css/styles.css"

interface HorSplitterProps {
  initHeight?: number
  onHeightChanged?: (height: number) => void
  children: ReactNode
}

export function HorSplitter({ 
  initHeight = 300, 
  onHeightChanged, 
  children 
}: HorSplitterProps) {
    
  const [height, setHeight] = useState(initHeight)

  useEffect(() => {
    if (onHeightChanged) {
      onHeightChanged(height)
    }
  }, [height, onHeightChanged])
  
  return (
    <ResizableBox
      width={Infinity}
      height={height}
      axis="y"
      onResize={(_, d) => setHeight(d.size.height)}
      minConstraints={[Infinity, 100]}
      maxConstraints={[Infinity, 600]}
      handle={
        <div 
          className="custom-resize-handle"
          style={{ 
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: 8,
            cursor: "row-resize",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "#394b59",
            borderTop: "1px solid #2F343C",
            borderBottom: "1px solid #2F343C",
            zIndex: 100,
          }} 
        >
          <GrDrag style={{ width: "16px", height: "8px" }} />
        </div>
      }
    >
        {children}
    </ResizableBox>
  )  
}