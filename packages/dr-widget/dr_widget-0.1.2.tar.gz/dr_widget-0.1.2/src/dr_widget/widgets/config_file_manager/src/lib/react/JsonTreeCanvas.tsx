import { useMemo } from "react";
import {
  Canvas,
  Edge,
  EdgeData,
  EdgeProps,
  Node,
  NodeData,
  NodeProps,
} from "reaflow";
import {
  TransformComponent,
  TransformWrapper,
} from "react-zoom-pan-pinch";

type JsonTreeCanvasProps = {
  data?: unknown;
};

type BuildResult = {
  nodes: NodeData[];
  edges: EdgeData[];
};

const formatPrimitive = (value: unknown): string => {
  if (typeof value === "string") {
    return `"${value}"`;
  }
  if (typeof value === "number" || typeof value === "bigint") {
    return `${value}`;
  }
  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }
  if (value === null) {
    return "null";
  }
  if (value === undefined) {
    return "undefined";
  }
  return String(value);
};

const createGraph = (input: unknown): BuildResult => {
  const nodes: NodeData[] = [];
  const edges: EdgeData[] = [];
  let idCounter = 0;
  let edgeCounter = 0;

  const createNode = (text: string, depth: number) => {
    const id = `node-${idCounter++}`;
    const lines = text.split("\n").length;
    const width = Math.min(Math.max(text.length * 8 + 32, 160), 320);
    const height = Math.max(lines * 22 + 20, 48);

    nodes.push({
      id,
      text,
      width,
      height,
      className:
        depth === 0
          ? "json-tree-node json-tree-node--root"
          : "json-tree-node",
      data: { depth, text },
      selectionDisabled: true,
    });

    return id;
  };

  const createEdge = (from: string, to: string) => {
    const id = `edge-${edgeCounter++}`;
    edges.push({
      id,
      from,
      to,
      className: "json-tree-edge",
      containerClassName: "json-tree-edge-container",
      selectionDisabled: true,
    });
  };

  const visit = (
    value: unknown,
    key: string,
    depth: number,
    parentId?: string,
  ) => {
    const isObject = value !== null && typeof value === "object";
    const isArray = Array.isArray(value);

    const baseLabel =
      depth === 0 ? "(root)" : key === "" ? "(item)" : key;

    let label = baseLabel;

    if (!isObject) {
      label = `${baseLabel}: ${formatPrimitive(value)}`;
    } else if (isArray) {
      label = `${baseLabel} [${(value as unknown[]).length}]`;
    } else {
      label = `${baseLabel} {${Object.keys(value as object).length}}`;
    }

    const currentId = createNode(label, depth);

    if (parentId) {
      createEdge(parentId, currentId);
    }

    if (!isObject) {
      return currentId;
    }

    const entries = isArray
      ? (value as unknown[]).map<[string, unknown]>((item, index) => [
          index.toString(),
          item,
        ])
      : Object.entries(value as Record<string, unknown>);

    if (entries.length === 0) {
      const emptyId = createNode("(empty)", depth + 1);
      createEdge(currentId, emptyId);
      return currentId;
    }

    for (const [childKey, childValue] of entries) {
      visit(childValue, childKey, depth + 1, currentId);
    }

    return currentId;
  };

  visit(input, "root", 0);

  return { nodes, edges };
};

export function JsonTreeCanvas({ data }: JsonTreeCanvasProps) {
  const { nodes, edges, error } = useMemo(() => {
    if (data === undefined) {
      return { nodes: [], edges: [], error: null as null | string };
    }

    try {
      const build = createGraph(data);
      return { ...build, error: null };
    } catch (err) {
      return {
        nodes: [],
        edges: [],
        error:
          err instanceof Error
            ? err.message
            : "Failed to render JSON graph.",
      };
    }
  }, [data]);

  const renderNode = (props: NodeProps<NodeData>) => <Node {...props} />;

  const renderEdge = (props: Partial<EdgeProps>) => <Edge {...props} />;

  if (data === undefined) {
    return (
      <div className="json-tree-placeholder">
        <p>Select a file to visualise the graph.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="json-tree-error">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <TransformWrapper
      minScale={0.2}
      maxScale={1.6}
      initialScale={0.8}
      wheel={{ step: 0.04 }}
      doubleClick={{ disabled: true }}
    >
      <TransformComponent
        wrapperStyle={{
          height: "100%",
          width: "100%",
          overflow: "hidden",
        }}
      >
        <Canvas
          nodes={nodes}
          edges={edges}
          height={Math.max(nodes.length * 140, 400)}
          width={Math.max(nodes.length * 120, 600)}
          maxHeight={1600}
          maxWidth={1600}
          animated={false}
          pannable={false}
          zoomable={false}
          fit={true}
          direction="RIGHT"
          node={renderNode}
          edge={renderEdge}
        />
      </TransformComponent>
    </TransformWrapper>
  );
}
