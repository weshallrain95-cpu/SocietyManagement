import type { PreregistrationChecklistItem } from "../types/preregistration";

interface Props {
  items: PreregistrationChecklistItem[];
  onToggle: (id: number, status: string) => void;
  onDelete: (templateId: number) => void;
}

export function ChecklistTable({ items, onToggle, onDelete }: Props) {
  if (!items.length) {
    return <p>No checklist items available.</p>;
  }

  return (
    <table
      style={{
        width: "100%",
        marginTop: "20px",
        borderCollapse: "collapse",
      }}
    >
      <thead>
        <tr>
          <th align="left">Done</th>
          <th align="left">Task</th>
          <th align="left">Mandatory</th>
        </tr>
      </thead>

      <tbody>
        {items.map((item) => {
          const hasDocument =
            item.document_uploaded &&
            item.document &&
            item.document.template_id;

          return (
            <tr key={item.id}>
              {/* CHECKBOX */}
              <td>
                <input
                  type="checkbox"
                  checked={item.status === "COMPLETED"}
                  onChange={() => onToggle(item.id, item.status)}
                />
              </td>

              {/* TASK + DOCUMENT */}
              <td>
                <div>{item.title}</div>

                {hasDocument && (
                  <div
                    style={{
                      marginTop: "6px",
                      fontSize: "13px",
                      background: "#f8f9fb",
                      padding: "8px",
                      borderRadius: "6px",
                    }}
                  >
                    <div>
                      Uploaded:{" "}
                      <a
                        href={item.document!.file}
                        target="_blank"
                        rel="noreferrer"
                      >
                        View document
                      </a>
                    </div>

                    <div style={{ marginTop: "6px" }}>
                      <button
                        onClick={() =>
                          onDelete(item.document!.template_id)
                        }
                        style={{ marginRight: "8px" }}
                      >
                        Delete
                      </button>

                      <button disabled>
                        Replace (coming next)
                      </button>
                    </div>
                  </div>
                )}
              </td>

              {/* MANDATORY */}
              <td>{item.mandatory ? "Yes" : "No"}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
