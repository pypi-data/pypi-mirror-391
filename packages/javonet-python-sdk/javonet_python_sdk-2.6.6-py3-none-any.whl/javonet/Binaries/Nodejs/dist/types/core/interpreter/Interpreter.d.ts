export class Interpreter {
    /** @type {Handler | null} */
    _handler: Handler | null;
    /** @type {Handler} */
    get handler(): Handler;
    /**
     *
     * @param {Command} command
     * @param {IConnectionData} connectionData
     * @returns
     */
    executeAsync(command: Command, connectionData: IConnectionData): Promise<import("../../utils/Command.js").Command>;
    /**
     *
     * @param {Command} command
     * @param {IConnectionData} connectionData
     * @returns {Command | Promise<Command>}
     */
    execute(command: Command, connectionData: IConnectionData): Command | Promise<Command>;
    /**
     *
     * @param {Uint8Array} messageByteArray
     * @returns {Promise<Command> | Command}
     */
    process(messageByteArray: Uint8Array): Promise<Command> | Command;
}
export type IConnectionData = import("../../utils/connectionData/IConnectionData.js").IConnectionData;
export type RuntimeNameType = typeof import("../../types.d.ts").RuntimeName;
export type Command = import("../../utils/Command.js").Command;
import { Handler } from '../handler/Handler.js';
