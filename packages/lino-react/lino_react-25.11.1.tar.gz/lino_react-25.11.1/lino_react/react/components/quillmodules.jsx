export const name = "quillmodules";

import { Mention, MentionBlot } from 'quill-mention';
import Quill from 'quill-next';
import Delta from "@quill-next/delta-es";
import { ClassAttributor, Scope } from "parchment";
import QuillNextEditor from "quill-next-react";
export { QuillNextEditor };
import { bubbleFormats } from "quill-next/dist/blots/block";
import { tableId } from "quill-next/dist/formats/table";
import Container from "quill-next/dist/blots/container";
import QuillImageDropAndPaste from 'quill-image-drop-and-paste';
import BlotFormatter from '@enzedonline/quill-blot-formatter2';
import htmlEditButton from "quill-html-edit-button";
import React from 'react';
import { RegisterImportPool } from "./Base";
import { debounce } from "./LinoUtils";

import "@enzedonline/quill-blot-formatter2/dist/css/quill-blot-formatter2.css"; // align styles

const NextTableModule = Quill.import("modules/table");
const NextTableCell = Quill.import("formats/table");
const NextTableRow = Quill.import("formats/table-row");
const NextTableContainer = Quill.import("formats/table-container");
// const TableBody = Quill.import("formats/table-body");

// const LinoCellClass = new ClassAttributor("linoCellClass", "lino-ql-cell", {scope: Scope.BLOCK});
// const LinoClass = new ClassAttributor("linoClass", "lino-ql", {scope: Scope.INLINE});

const TableClasses = {}


const USE_INLINE_MOD = false;
const PARTIAL_INLINE_MOD = false;


let TableCell;

if (USE_INLINE_MOD) {

    TableCell = class TableCell extends NextTableCell {
        /**
         * Accept either a row id string, or an object { row?: string, class?: string }
         * so callers can pass both the data-row value and className to preserve classes.
         */
        static create(value) {
            let node;
            if (typeof value === "string" || value == null) {
                node = super.create(value);
            } else {
                node = super.create(value.row);

                if (value.class) {
                    node.setAttribute("class", value.class);
                }
            }
            return node;
        }

        static formats(domNode, scroll) {
            const formats = {};
            formats.row = super.formats(domNode, scroll);
            if (domNode.hasAttribute("class")) {
                const klass = domNode.getAttribute("class");
                if (klass.length) formats.class = klass;
            }
            return formats;
        }


        formats() {
            return TableCell.formats(this.domNode);
        }

        format(name, value) {
            if (name === TableCell.blotName) {
                if (typeof value === "string") {
                    super.format(name, value);
                } else
                if (typeof value === "object" && value !== null) {
                    super.format(name, value.row);
                    _format(this.domNode, value);
                }
            } else {
                super.format(name, value);
            }
        }

        // optimize(...args) {
        //     console.log("tablecell.optimize", args, bubbleFormats(this));
        //     super.optimize(...args)
        // }
    }
} else {
    TableCell = class TableCell extends NextTableCell {
        static create(value) {
            console.log("TableCell.create", value);
            return super.create(value);
        }

        static formats(domNode, scroll) {
            console.log("TableCell.formats", domNode);
            return super.formats(domNode, scroll);
        }

        formats() {
            console.log("tablecell.formats");
            return super.formats();
        }

        format(name, value) {
            console.log("tablecell.format", name, value);
            super.format(name, value);
        }
    }
}


function tableID() {
    return "table-" + Math.random().toString(36).slice(2, 6);
}


function _formats(domNode) {
    const formats = {};
    if (domNode.hasAttribute("data-id"))
        formats.id = domNode.getAttribute("data-id");
    if (domNode.hasAttribute("class"))
        formats.class = domNode.getAttribute("class");
    if (Object.keys(formats).length) return formats;
    return undefined;
}


function _format(domNode, value) {
    if (value.id && value.id.length) {
        const id = domNode.getAttribute("data-id");
        if (id !== value.id)
            domNode.setAttribute("data-id", value.id);
    }
    if (value.class && value.class.length) {
        const klass = domNode.getAttribute("class");
        if (klass !== value.class)
            domNode.setAttribute("class", value.class);
    } else {
        if (domNode.hasAttribute("class"))
            domNode.removeAttribute("class");
    }
}

let TableRow;

if (USE_INLINE_MOD) {
    TableRow = class TableRow extends NextTableRow {
        /**
         * Accept either a className string or an object { class?: string } so callers
         * can pass classes when programmatically creating a row.
         */
        static create(value, ...args) {
            const node = super.create();
            if (typeof value === 'object' && value !== null) {
                _format(node, value);
            }
            return node;
        }

        static formats(domNode, scroll) {
            const rowFormats = _formats(domNode) || {};
            let rowId = rowFormats.id || domNode.children[0]
                .getAttribute("data-row");
            if (!rowFormats.id) rowFormats.id = rowId;
            if (rowId in TableClasses) {
                TableClasses[TableClasses[rowId]][rowId] = rowFormats;
                return rowFormats;
            }
            const tFormats = TableContainer.formats(
                domNode.parentElement.parentElement) || {};
            const tId = tFormats.id || tableID();
            const formats = TableClasses[tId] = {};
            TableClasses[rowId] = tId;
            formats[tId] = tFormats;
            if (!tFormats.id) tFormats.id = tId;
            formats[rowId] = rowFormats;

            let _domNode = domNode.nextSibling;
            while (_domNode) {
                rowId = _domNode.children[0].getAttribute("data-row");
                TableClasses[rowId] = tId;
                formats[rowId] = _formats(_domNode) || {};
                if (!formats[rowId].id) formats[rowId].id = rowId;
                _domNode = _domNode.nextSibling;
            }

            return rowFormats;
        }

        /**
         * Instance formats include existing block formats plus an explicit key for row
         * classes so callers can inspect both.
         */
        formats() {
            return _formats(this.domNode);
        }


        /**
         * Allow:
         * - row.format('table-row', 'my-class')  // convenience (treat 'table-row' as class setter)
         * - row.format('table-row-class', 'my-class another') // explicit
         */
        format(name, value) {
            if (name === TableRow.blotName) {
                if (value) _format(this.domNode, value);
            } else {
                super.format(name, value);
            }
        }

        optimize(...args) {
            console.log("TableRow.optimize", args);
            if (!("counter" in TableClasses)) TableClasses.counter = 0;
            TableClasses.counter++;
            if (TableClasses.counter > 50) {
                TableClasses.counter = 0;
                throw new Error("Maximum recursion occured!");
            }
            Container.prototype.optimize.call(this, ...args);
            this.children.forEach((child) => {
                if (child.next == null) return;
                const childFormats = child.formats();
                const nextFormats = child.next.formats();
                if (childFormats.row !== nextFormats.row) {
                    const next = this.splitAfter(child);
                    if (next) {
                        next.optimize();
                    }
                    // We might be able to merge with prev now
                    if (this.prev) {
                        this.prev.optimize();
                    }
                }
            });
            const firstCell = this.children.head;
            if (!firstCell) return;
            const formats = _formats(this.domNode);
            let rowId = formats && formats.id;
            if (!rowId) rowId = firstCell.domNode.getAttribute("data-row");
            console.log(rowId);
            const tId = TableClasses[rowId];
            console.log(tId, TableClasses);
            if (!tId) return;
            this.format(TableRow.blotName, TableClasses[tId][rowId]);
        }
    }
} else {
    TableRow = class TableRow extends NextTableRow {
        static create(value) {
            console.log("TableRow.create", value);
            const node = super.create();
            if (value) node.setAttribute("class", value);
            return node;
        }

        static formats(domNode, scroll) {
            console.log("TableRow.formats", domNode);
            if (domNode.hasAttribute("class")) {
                return domNode.getAttribute("class")
            }
            return undefined;
        }

        formats() {
            console.log("tablerow.formats");
            return TableRow.formats(this.domNode);
        }

        format(name, value) {
            console.log("tablerow.format", name, value);
            if (name === TableRow.blotName && value) {
                this.domNode.setAttribute('class', value);
            } else {
                super.format(name, value);
            }
        }
    }
}


class TableContainer extends NextTableContainer {

    // static create(value) {
    //     const node = super.create(value);
    //     console.log("TableContainer.create", node.children);
    //     return node;
    // }

    static formats(domNode) {
        return _formats(domNode);
    }

    format(name, value) {
        if (name === TableContainer.blotName) {
            if (value) {
                _format(this.domNode, value);
            }
        } else {
            super.format(name, value);
        }
    }

    optimize(...args) {
        console.log("TableContainer.optimize", args);
        super.optimize(...args);
        const tbody = this.children.head;
        if (!tbody) return;
        const formats = _formats(this.domNode);
        const rowId = tbody.children.head.children.head.domNode.getAttribute("data-row");
        let tId = formats && formats.id;
        if (!tId) {
            tId = TableClasses[rowId];
        }
        if (!tId) return;
        // _format(this.domNode, TableClasses[tId][tId]);
        this.format(TableContainer.blotName, TableClasses[tId][tId]);

        tbody.children.forEach(row => {
            const rowFormats = _formats(row.domNode);
            let rowId = rowFormats && rowFormats.id;
            if (!rowId)
                rowId = row.children.head.domNode.getAttribute("data-row");
            row.format(TableRow.blotName, TableClasses[tId][rowId]);
            // _format(row.domNode, TableClasses[tId][rowId]);
        });
    }

    balanceCells() {
        const rows = this.descendants(TableRow);
        const maxColumns = rows.reduce((max, row) => {
            return Math.max(row.children.length, max);
        }, 0);
        rows.forEach((row) => {
            new Array(maxColumns - row.children.length).fill(0).forEach(() => {
                let value = null;
                if (row.children.head != null) {
                    value = TableCell.formats(row.children.head.domNode);
                }
                // Pass an object so the new cell keeps both data-row and class
                const blot = this.scroll.create(TableCell.blotName, value);
                row.appendChild(blot);
                blot.optimize(); // Add break blot
            });
        });
    }

    insertColumn(index) {
        const [body] = this.descendant(TableBody);
        if (body == null || body.children.head == null) return;
        body.children.forEach((row) => {
            const ref = row.children.at(index);
            const value = TableCell.formats(ref.domNode);
            const cell = this.scroll.create(TableCell.blotName, value);
            row.insertBefore(cell, ref);
        });
    }

    insertRow(index) {
        const [body] = this.descendant(TableBody);
        if (body == null || body.children.head == null) return;
        const id = tableId();
        // copy row classes from first body row if present
        const templateRow = body.children.head;
        const templateRowClass = templateRow && templateRow.domNode ? templateRow.domNode.getAttribute('class') : undefined;
        const rowFormats = {id};
        if (templateRowClass && templateRowClass.length)
            rowFormats.class = templateRowClass;
        const row = this.scroll.create(TableRow.blotName, rowFormats);
        body.children.head.children.forEach(() => {
            // preserve classes on created cells from the template cell
            const headCell = templateRow.children.head;
            const cellClass = headCell && headCell.domNode ? headCell.domNode.getAttribute('class') : undefined;
            const cell = this.scroll.create(TableCell.blotName, { row: id, class: cellClass || undefined });
            row.appendChild(cell);
        });
        const ref = body.children.at(index);
        body.insertBefore(row, ref);
    }
}

//
// function applyFormat(delta, format, value, scroll) {
//     if (!scroll.query(format)) {
//         return delta;
//     }
//
//     return delta.reduce((newDelta, op) => {
//         if (!op.insert) return newDelta;
//         if (op.attributes && op.attributes[format]) {
//             return newDelta.push(op);
//         }
//         const formats = value ? { [format]: value } : {};
//         return newDelta.insert(op.insert, { ...formats, ...op.attributes });
//     }, new Delta());
// }
//
//
// function matchTable(node, delta, scroll) {
//     console.log("matchTable", node, JSON.stringify(delta), scroll);
//     const table =
//         node.parentElement?.tagName === 'TABLE'
//         ? node.parentElement
//         : node.parentElement?.parentElement;
//     if (table != null) {
//         const rows = Array.from(table.querySelectorAll('tr'));
//         const row = rows.indexOf(node) + 1;
//
//         // capture class name (if any) from the table element
//         // const className = (table.getAttribute && table.getAttribute('class')) || table.className || undefined;
//
//         // First, apply the 'table' format as before (if supported)
//         const formatted = applyFormat(delta, 'table', row, scroll);
//
//         // If there's a className, add it into op.attributes.className for each insert op
//         // if (className) {
//         //     return formatted.reduce((newDelta, op) => {
//         //         if (!op.insert) return newDelta;
//         //         const attrs = { ...(op.attributes || {}) };
//         //         if (attrs.className == null) {
//         //             // add className attribute when not already present
//         //             // keep existing attributes intact
//         //             attrs.className = className;
//         //         }
//         //         return newDelta.insert(op.insert, attrs);
//         //     }, new Delta());
//         // }
//
//         return formatted;
//     }
//     return delta;
// }


class TableModule extends NextTableModule {
    insertTable(rows, columns) {
        const range = this.quill.getSelection();
        if (range == null) return;
        const delta = new Array(rows).fill(0).reduce((memo) => {
          const text = new Array(columns).fill('\n').join('');
          return memo.insert(text, {table: {row: tableId()}});
        }, new Delta().retain(range.index));
        this.quill.updateContents(delta, Quill.sources.USER);
        this.quill.setSelection(range.index, Quill.sources.SILENT);
        this.balanceTables();
    }
}


Quill.register('modules/imageDropAndPaste', QuillImageDropAndPaste);
Quill.register('modules/blotFormatter2', BlotFormatter);
Quill.register({"blots/mention": MentionBlot, "modules/mention": Mention});
Quill.register('modules/htmlEditButton', htmlEditButton);

if (USE_INLINE_MOD || PARTIAL_INLINE_MOD) {
    // Quill.register(TableCell);
    // Quill.register(TableRow);
    // Quill.register(TableContainer);
    Quill.register('formats/table-row', TableRow);
    Quill.register('formats/table', TableCell);
    if (USE_INLINE_MOD) {
        Quill.register('formats/table-container', TableContainer);
        Quill.register('modules/table', TableModule);
    }
}

// Quill.register({"attributors/class/linoClass": LinoClass}, true);
// Quill.register({"formats/linoClass": LinoClass}, true);
// Quill.register({"attributors/class/linoCellClass": LinoCellClass}, true);
// Quill.register({"formats/linoCellClass": LinoCellClass}, true);

const QuillImageData = QuillImageDropAndPaste.ImageData;

let ex; const exModulePromises = ex = {
    queryString:  import(/* webpackChunkName: "queryString_quillmodules" */"query-string"),
};RegisterImportPool(ex);


const applyClasses = (classes, domNode) => {
    let current = Array.from(domNode.classList);

    current.forEach((classname) => {
        if (!classes.includes(classname))
            domNode.classList.remove(classname);
    });
    current = Array.from(domNode.classList);

    classes.forEach((classname) => {
        if (!current.includes(classname))
            domNode.classList.add(classname);
    });
}


export const tableContextMenuProps = (elem) => {
    const { i18n } = elem.ex;

    const module = () => {
        elem.quill.focus();
        return elem.quill.getModule("table");
    }

    const model = [
        {
            command: (e) => {
                module().insertColumnLeft();
            },
            icon: <span>&nbsp;⭰&nbsp;</span>,
            label: i18n.t("Insert column left"),
        },
        {
            command: (e) => {
                module().insertColumnRight();
            },
            icon: <span>&nbsp;⭲&nbsp;</span>,
            label: i18n.t("Insert column right"),
        },
        {
            command: (e) => {
                module().insertRowAbove();
            },
            icon:  <span>&nbsp;⭱&nbsp;</span>,
            label: i18n.t("Insert row above"),
        },
        {
            command: (e) => {
                module().insertRowBelow();
            },
            icon: <span>&nbsp;⭳&nbsp;</span>,
            label: i18n.t("Insert row below"),
        },
        {
            command: (e) => {
                module().deleteColumn();
            },
            icon: "pi pi-delete-left",
            label: i18n.t("Delete column"),
        },
        {
            command: (e) => {
                module().deleteRow();
            },
            icon: "pi pi-eraser",
            label: i18n.t("Delete row"),
        },
        {
            command: (e) => {
                module().deleteTable();
            },
            icon: "pi pi-trash",
            label: i18n.t("Delete table"),
        },
        {
            command: (e) => {
                const [table, row, cell] = module().getTable();
                const ctx = elem.c;
                let tableClasses = i18n.t("Comma separated TABLE clsasses"),
                    rowClasses = i18n.t("Comma separated TR classes"),
                    cellClasses = i18n.t("Comma separated TD classes"),
                    applyToAllRow = i18n.t("Apply to all row?"),
                    applyToAllCell = i18n.t("Apply to all cell?"),
                    applyToAllCellOfThisRow = i18n.t("Apply to all cell of this row?"),
                    title = i18n.t("Manage classes"),
                    agreeLabel = i18n.t("Apply");

                const ok = (data) => {
                    const tcs = data[tableClasses].split(",")
                        .filter(item => !!item).join(" ").trim();

                    if (USE_INLINE_MOD) {
                        const tableFormats = _formats(table.domNode);
                        if (tcs && tcs !== tableFormats.class) {
                            tableFormats.class = tcs;
                            TableClasses[tableFormats.id][tableFormats.id] = tableFormats;
                            _format(table.domNode, tableFormats)
                        }
                    } else {
                        const splitted = tcs.split(" ").filter(item => !!item);
                        if (splitted.length > 0)
                            applyClasses(splitted, table.domNode);
                    }

                    const formatRow = (classes, row) => {
                        if (USE_INLINE_MOD) {
                            const rowFormats = _formats(row.domNode)
                            if (classes && classes !== rowFormats.class) {
                                rowFormats.class = classes;
                                TableClasses[tableFormats.id][rowFormats.id] = rowFormats;
                                _format(row.domNode, rowFormats);
                            }
                        } else if (PARTIAL_INLINE_MOD) {
                            console.log("calling formatLine");
                            const index = elem.quill.getIndex(row);
                            elem.quill.formatLine(index, 1, TableRow.blotName, classes);
                        } else {
                            const splited = classes.split(" ").filter(item => !!item);
                            if (splited.length > 0)
                                applyClasses(splited, row.domNode);
                        }
                    }

                    const rcs = data[rowClasses].split(",")
                    .filter(item => !!item).join(" ").trim();

                    formatRow(rcs, row);
                    let _row;
                    if (data[applyToAllRow]) {
                        _row = row.prev;
                        while (_row !== null) {
                            formatRow(rcs, _row);
                            _row = _row.prev;
                        }
                        _row = row.next;
                        while (_row !== null) {
                            formatRow(rcs, _row);
                            _row = _row.next;
                        }
                    }

                    const allCell = data[applyToAllCell];
                    let _cell, ccs = data[cellClasses].split(",")
                        .filter(item => !!item);
                    applyClasses(ccs, cell.domNode);

                    if (allCell || data[applyToAllCellOfThisRow]) {
                        _cell = cell.prev;
                        while (_cell !== null) {
                            applyClasses(ccs, _cell.domNode);
                            _cell = _cell.prev;
                        }
                        _cell = cell.next;
                        while (_cell !== null) {
                            applyClasses(ccs, _cell.domNode);
                            _cell = _cell.next;
                        }
                    }

                    if (allCell) {
                        _row = row.prev;
                        while (_row !== null) {
                            _cell = _row.children.head;
                            if (_cell.prev !== null) {
                                throw new Error("Programming error, row.children.head returned cell with prev item")
                            }
                            while (_cell !== null) {
                                applyClasses(ccs, _cell.domNode);
                                _cell = _cell.next;
                            }
                            _row = _row.prev;
                        }

                        _row = row.next;
                        while (_row !== null) {
                            _cell = _row.children.head;
                            if (_cell.prev !== null) {
                                throw new Error("Programming error, row.children.head returned cell with prev item")
                            }
                            while (_cell !== null) {
                                applyClasses(ccs, _cell.domNode);
                                _cell = _cell.next;
                            }
                            _row = _row.next;
                        }
                    }
                    return true;
                }

                ctx.APP.dialogFactory.createParamDialog(ctx, {
                    [tableClasses]: {
                        default: Array.from(table.domNode.classList).join(","),
                        react_name: "CharFieldElement",
                    },
                    [rowClasses]: {
                        default: Array.from(row.domNode.classList).join(","),
                        react_name: "CharFieldElement",
                    },
                    [applyToAllRow]: {
                        default: false,
                        react_name: "BooleanFieldElement",
                    },
                    [cellClasses]: {
                        default: Array.from(cell.domNode.classList).join(","),
                        react_name: "CharFieldElement",
                    },
                    [applyToAllCellOfThisRow]: {
                        default: false,
                        react_name: "BooleanFieldElement",
                    },
                    [applyToAllCell]: {
                        default: false,
                        react_name: "BooleanFieldElement",
                    },
                }, title, ok, agreeLabel);
            },
            icon: <span>&nbsp;🄿&nbsp;</span>,  // \u1F13F
            label: i18n.t("Properties"),
        },
    ]
    return {model}
}


export const onRightClick = (elem) => {
    if (elem.state.plain) return null;
    return (e) => {
        const { quill } = elem;
        const tableModule = quill.getModule("table");
        const [table] = tableModule.getTable();
        if (table !== null) {
            e.preventDefault();
            elem.tableContextMenu.show(e);
        }
    }
}


export const quillLoad = (elem, quill) => {
    const value = elem.getValue();
    if (elem.state.plain) {
        quill.setText(value || "");
    } else {
        quill.clipboard.dangerouslyPasteHTML(value);
    }
}


export const onTextChange = (elem, e) => {
    // console.log("onTextChange", e);
    // cleans up the trailing new line (\n)
    const plainValue = e.textValue.slice(0, -1);
    let value = (elem.state.plain ? plainValue : e.htmlValue ) || "";
    elem.update({[elem.dataKey]: value});
    // elem.setState({})
}


export const getQuillModules = (
    APP, silentFetch, signal, mentionValues, i18n, elem, hasToolbar = true
) => {
    const toolbarID = `l-ql-toolbar-${elem.props.elem.name}`;
    const modules = {
        toolbar: `#${toolbarID}`,
        mention: quillMention({
            silentFetch: silentFetch,
            signal: signal,
            mentionValues: mentionValues,
        }),
        blotFormatter2: {
            debug: true,
            resize: {
                useRelativeSize: true,
            },
            video: {
                registerBackspaceFix: false
            }
        },
        table: true,
    }
    if (hasToolbar) {
        modules.htmlEditButton = {
            msg: i18n.t('Edit HTML here, when you click "OK" the quill editor\'s contents will be replaced'),
            prependSelector: "div#raw-editor-container",
            okText: i18n.t("Ok"),
            cancelText: i18n.t("Cancel"),
            buttonTitle: i18n.t("Show HTML source"),
        }
    }
    if (APP.state.site_data.installed_plugins.includes('uploads'))
        modules.imageDropAndPaste = {handler: imageHandler(elem)};
    modules.keyboard = {
        bindings: {
            home: {
                key: "Home",
                shiftKey: null,
                handler: function (range, context) {
                    const { quill } = elem;
                    let [line, offset] = quill.getLine(range.index);
                    if (line && line.domNode.tagName === "LI") {
                      // Move to the start of text inside the list item
                      if (context.event.shiftKey) {
                          const index = line.offset(quill.scroll);
                          quill.setSelection(index, range.index - index, "user");
                      } else {
                          quill.setSelection(line.offset(quill.scroll), 0, "user");
                      }
                      return false; // stop default browser behavior
                    }
                    return true;
                },
            },
        }
    }

    // Disable "- " from creating a bullet list or any other autofill.
    // https://github.com/slab/quill/blob/539cbffd0a13b18e9c65eb84dd35e6596e403158/packages/quill/src/modules/keyboard.ts#L550
    if (elem.state.plain) modules.keyboard.bindings["list autofill"] = false;

    if (!hasToolbar) delete modules.toolbar;

    modules.clipboard = {
        matchers: [
            // ["tr", matchTable],
        ]
    }

    const meta = {toolbarID};

    return {modules, meta};
}


export const changeDelta = (elem) => {
    return (delta, oldContents, source) => {
        // copied from primereact/components/lib/editor/Editor.js
        const quill = elem.quill;
        let firstChild = quill.container.children[0];
        let html = firstChild ? firstChild.innerHTML : null;
        let text = quill.getText();

        if (html === '<p><br></p>') {
            html = null;
        }

        // GitHub primereact #2271 prevent infinite loop on clipboard paste of HTML
        if (source === 'api') {
            const htmlValue = quill.container.children[0];
            const editorValue = document.createElement('div');

            editorValue.innerHTML = elem.getValue() || '';

            // this is necessary because Quill rearranged style elements
            if (elem.ex.prUtils.DomHandler.isEqualElement(htmlValue, editorValue)) {
                return;
            }
        }

        onTextChange(elem, {
            htmlValue: html,
            textValue: text,
            delta: delta,
            source: source
        });
    }
}


export const overrideImageButtonHandler = (quill) => {
    quill.getModule('toolbar').addHandler('image', (clicked) => {
        if (clicked) {
            let fileInput;
            // fileInput = quill.container.querySelector('input.ql-image[type=file]');
            // if (fileInput == null) {
                fileInput = document.createElement('input');
                fileInput.setAttribute('type', 'file');
                fileInput.setAttribute('accept', 'image/png, image/gif, image/jpeg, image/bmp, image/x-icon');
                fileInput.classList.add('ql-image');
                fileInput.addEventListener('change', (e) => {
                    const files = e.target.files;
                    let file;
                    if (files.length > 0) {
                        file = files[0];
                        const type = file.type;
                        const reader = new FileReader();
                        reader.onload = (e) => {
                            const dataURL = e.target.result;
                            imageHandler({quill})(
                                dataURL,
                                type,
                                new QuillImageData(dataURL, type, file.name)
                            );
                            fileInput.value = '';
                        }
                        reader.readAsDataURL(file);
                    }
                })
            // }
            fileInput.click();
        }
    })
}

export const imageHandler = (elem) => {
    return (imageDataURL, type, imageData) => {
        const quill = elem.quill;
        let index = (quill.getSelection() || {}).index;
        if (index === undefined || index < 0) index = quill.getLength();
        quill.insertEmbed(index, 'image', imageDataURL);
        // quill.insertEmbed(index, 'image', imageData.toFile());
    }

    // const imageEl = quill.root.querySelector(`img[src="${imageDataURL}"]`);
    // Set default height
    // imageEl.setAttribute("height", window.App.URLContext.root.chInPx.offsetHeight * 20);
}

export const quillMention = ({silentFetch, signal, mentionValues}) => {
    function mentionSource(searchTerm, renderList, mentionChar) {
        if (searchTerm.length === 0) {
            let values = mentionValues[mentionChar];
            renderList(values, searchTerm);
        } else {
            ex.resolve(['queryString']).then(({queryString}) => {
                silentFetch({path: `suggestions?${queryString.default.stringify({
                    query: searchTerm, trigger: mentionChar})}`, signal: signal})
                .then(data => renderList(data.suggestions, searchTerm));
            });
        }
    }

    return {
        allowedChars: /^[A-Za-z0-9\s]*$/,
        mentionDenotationChars: window.App.state.site_data.suggestors,
        source: mentionSource,
        listItemClass: "ql-mention-list-item",
        mentionContainerClass: "ql-mention-list-container",
        mentionListClass: "ql-mention-list",
        dataAttributes: ["value", "link", "title", "denotationChar"],
    }
}

const quillToolbarHeaderTemplate = <React.Fragment>
    <span className="ql-formats">
        <select className='ql-header' defaultValue='0'>
            <option value='1'>Header 1</option>
            <option value='2'>Header 2</option>
            <option value='3'>Header 3</option>
            <option value='4'>Header 4</option>
            <option value='0'>Normal</option>
        </select>
        <select className='ql-font'>
            <option defaultValue={true}></option>
            <option value='serif'></option>
            <option value='monospace'></option>
        </select>
    </span>
    <span className="ql-formats">
        <select className="ql-size">
            <option value="small"></option>
            <option defaultValue={true}></option>
            <option value="large"></option>
            <option value="huge"></option>
        </select>
    </span>
    <span className="ql-formats">
        <button className="ql-script" value="sub"></button>
        <button className="ql-script" value="super"></button>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-bold' aria-label='Bold'></button>
        <button type='button' className='ql-italic' aria-label='Italic'></button>
        <button type='button' className='ql-underline' aria-label='Underline'></button>
    </span>
    <span className="ql-formats">
        <select className='ql-color'></select>
        <select className='ql-background'></select>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-list' value='ordered' aria-label='Ordered List'></button>
        <button type='button' className='ql-list' value='bullet' aria-label='Unordered List'></button>
        <select className='ql-align'>
            <option defaultValue={true}></option>
            <option value='center'></option>
            <option value='right'></option>
            <option value='justify'></option>
        </select>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-link' aria-label='Insert Link'></button>
        <button type='button' className='ql-image' aria-label='Insert Image'></button>
        <button type='button' className='ql-code-block' aria-label='Insert Code Block'></button>
    </span>
    <span className="ql-formats">
        <button type='button' className='ql-clean' aria-label='Remove Styles'></button>
    </span>
</React.Fragment>

export const invokeRefInsert = (elem) => {
    const { APP } = elem.props.urlParams.controller;
    const { URLContext } = APP;
    let index = (elem.quill.getSelection() || {}).index;
    if (index === undefined || index < 0)
        index = elem.quill.getLength();
    URLContext.actionHandler.runAction({
        action_full_name: URLContext.actionHandler.findUniqueAction("insert_reference").full_name,
        actorId: "about.About",
        response_callback: (data) => {
            if (data.success)
                elem.quill.insertText(index, data.message);
        }
    });
}

export const refInsert = (elem) => {
    if (!elem.c.APP.state.site_data.installed_plugins.includes('memo'))
        return null;
    return <span className="ql-formats">
        <button type='button'
            onClick={(e) => invokeRefInsert(elem)}
            aria-label='Open link dialog'>
            <i className="pi pi-link"></i></button>
    </span>
}

const commonHeader = (elem) => {
    return <>
        {quillToolbarHeaderTemplate}
        {refInsert(elem)}
        {
        <span className="ql-formats">
            <button type="button"
                onClick={e => {
                    const ctx = elem.props.urlParams.controller;
                    const title = elem.ex.i18n.t("rows x columns");
                    const rows_text = elem.ex.i18n.t("Rows");
                    const columns_text = elem.ex.i18n.t("Columns");
                    const ok = (data) => {
                        const rows = parseInt(data[rows_text]);
                        const cols = parseInt(data[columns_text]);
                        const rowsNaN = elem.ex.u.isNaN(rows);
                        if (rowsNaN || elem.ex.u.isNaN(cols)) {
                            ctx.APP.toast.show({
                                severity: "warn",
                                summary: elem.ex.i18n.t("Not a number '{{dir}}'",
                                    {dir: rowsNaN
                                        ? elem.ex.i18n.t("rows")
                                        : elem.ex.i18n.t("columns")}),
                            });
                            return false;
                        }
                        const t = elem.quill.getModule("table");
                        elem.quill.focus();
                        TableClasses.counter = 0;
                        t.insertTable(rows, cols);
                        return true;
                    }
                    ctx.APP.dialogFactory.createParamDialog(ctx, {
                        [rows_text]: {
                            react_name: "IntegerFieldElement",
                            default: 3,
                        },
                        [columns_text]: {
                            react_name: "IntegerFieldElement",
                            default: 3,
                        }
                    }, title, ok);
                }}>
                <i className="pi pi-table"></i></button>
        </span>
        }
    </>
}

export const quillToolbar = {
    header: quillToolbarHeaderTemplate,
    commonHeader: commonHeader,
}
