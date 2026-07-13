"use client";

import { ChevronDown, ChevronLeft, ChevronRight, ChevronUp, ChevronsUpDown, Database, Search } from "lucide-react";
import { flexRender, getCoreRowModel, getFilteredRowModel, getPaginationRowModel, getSortedRowModel, useReactTable, type ColumnDef, type SortingState } from "@tanstack/react-table";
import { useMemo, useState, type ReactNode } from "react";

export interface DenseColumn<T extends object> {
  key: keyof T | string;
  label: string;
  render?: (row: T) => ReactNode;
}

export function DenseTable<T extends object>({rows, columns, searchPlaceholder = "Search rows", compact = false}: {rows: T[]; columns: DenseColumn<T>[]; searchPlaceholder?: string; compact?: boolean}) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [filter, setFilter] = useState("");
  const [pagination, setPagination] = useState({pageIndex: 0, pageSize: 20});
  const defs = useMemo<ColumnDef<T>[]>(() => columns.map((column) => ({
    id: String(column.key),
    accessorFn: (row) => (row as Record<string, unknown>)[String(column.key)],
    enableGlobalFilter: true,
    header: column.label,
    cell: (context) => column.render ? column.render(context.row.original) : String(context.getValue() ?? "N/A"),
  })), [columns]);
  // TanStack Table deliberately exposes mutable callbacks; React Compiler skips this hook.
  // eslint-disable-next-line react-hooks/incompatible-library
  const table = useReactTable({
    data: rows,
    columns: defs,
    state: {sorting, globalFilter: filter, pagination},
    onSortingChange: setSorting,
    onGlobalFilterChange: setFilter,
    onPaginationChange: setPagination,
    getColumnCanGlobalFilter: () => true,
    globalFilterFn: (row, columnId, value) => searchable(row.getValue(columnId)).includes(String(value).trim().toLocaleLowerCase()),
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });
  const filteredCount = table.getFilteredRowModel().rows.length;
  const pageCount = Math.max(1, table.getPageCount());
  const firstRow = filteredCount ? pagination.pageIndex * pagination.pageSize + 1 : 0;
  const lastRow = filteredCount ? Math.min(filteredCount, firstRow + table.getRowModel().rows.length - 1) : 0;
  return <div className={`dense-table-wrap ${compact ? "is-compact" : ""}`}>
    <label className="table-search"><Search aria-hidden="true" /><span className="sr-only">{searchPlaceholder}</span><input value={filter} onChange={(event) => setFilter(event.target.value)} placeholder={searchPlaceholder} /></label>
    {filteredCount ? <div className="table-scroll"><table><thead>{table.getHeaderGroups().map((group) => <tr key={group.id}>{group.headers.map((header) => <th key={header.id}><button onClick={header.column.getToggleSortingHandler()}>{flexRender(header.column.columnDef.header, header.getContext())}{header.column.getIsSorted() === "asc" ? <ChevronUp /> : header.column.getIsSorted() === "desc" ? <ChevronDown /> : <ChevronsUpDown />}</button></th>)}</tr>)}</thead><tbody>{table.getRowModel().rows.map((row) => <tr key={row.id}>{row.getVisibleCells().map((cell) => <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>)}</tr>)}</tbody></table></div> : <div className="table-empty-state"><Database aria-hidden="true" /><strong>NO COMMITTED EVIDENCE ROWS MATCH THIS VIEW</strong></div>}
    <div className="table-footer"><span className="table-count">{firstRow}-{lastRow} / {filteredCount} filtered / {rows.length} rows</span><div className="pagination-controls"><button className="icon-button" aria-label="Previous table page" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}><ChevronLeft aria-hidden="true" /></button><span>Page {pagination.pageIndex + 1} of {pageCount}</span><button className="icon-button" aria-label="Next table page" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}><ChevronRight aria-hidden="true" /></button></div></div>
  </div>;
}

function searchable(value: unknown): string {
  if (value == null) return "";
  if (typeof value === "object") return Object.values(value as Record<string, unknown>).map(searchable).join(" ");
  return String(value).toLocaleLowerCase();
}
