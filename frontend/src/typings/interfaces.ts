export interface IUserState {
    authorized: boolean;
    username: string;
    adminRole: boolean;
}

// для каждой таблицы сущности
// например, для inventoryitem интерфейс {}
enum itemCategory {
    'МОНОБЛОК',
    'ПРИНТЕР',
    'НОУТБУК',
    'КОМПЬЮТЕР',
    'МЕБЕЛЬ'
}

enum userType {
    'ADMIN',
    'READER'
}

enum inquiryStatus {
    'new',
    'queued',
    'finished'
}

export interface IInventoryItem {
    id: number;
    invid: string;
    category: itemCategory;
    displayName: string;
    serialNum: string;
    price: number;
    available: boolean;
}

export interface IInquiry {
    id: number;
    inquirerName: string;
    inquirerEmail: string;
    comment: string;
    status: inquiryStatus;
    invid: IInventoryItem["invid"];
    itemName: IInventoryItem["displayName"];
}

export interface ILog {
    id: number;
    itemId: IInventoryItem['invid'];
    timestamp: Date;
    description: string;
    author: IUser;
}

export interface IUser {
    id: number;
    userType: userType;
    displayName: string;
}

export interface IFile {
    id: number;
    fileName: string;
}

export interface requestResponse {
    success: boolean;
    errorMessage?: string;
    data?: any;
}