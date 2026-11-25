pragma Singleton
import QtQuick

QtObject {
    function env(name: string): string { return ""; }
    function shellPath(rel: string): string { return rel; }
    function execDetached(args: var) {}
}
