export interface IUserState {
  authorized: boolean;
  username: string;
  adminRole: boolean;
}

// для каждой таблицы сущности
// например, для inventoryitem интерфейс {}
export enum itemCategory {
  "МОНОБЛОК",
  "ПРИНТЕР",
  "НОУТБУК",
  "КОМПЬЮТЕР",
  "МЕБЕЛЬ",
}

export enum userType {
  "ADMIN",
  "READER",
}

export enum inquiryStatus {
  "new",
  "queued",
  "finished",
}

export interface IInventoryItem {
  id: number;
  invid: string;
  category: itemCategory;
  displayName: string;
  description: string;
  serial_num: string;
  price: number;
  available: boolean;
}

export interface IInquiry {
  id?: number;
  inquirerName: string;
  inquirerEmail: string;
  comment: string;
  status: inquiryStatus;
  itemId: IInventoryItem["id"];
}

export interface ILog {
  id: number;
  itemId: IInventoryItem["id"];
  timestamp: string;
  description: string;
  files: IFile[];
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

interface RequestResponseFail {
  success: false;
  errorMessage: string;
}

interface RequestResponseSuccess<ResponseDataType> {
  success: true;
  data: ResponseDataType;
}

export type RequestResponse<ResponseDataType> =
  | RequestResponseFail
  | RequestResponseSuccess<ResponseDataType>;
