import { TestBed } from '@angular/core/testing';

import { DatalinkService } from './datalink.service';

describe('DatalinkService', () => {
  let service: DatalinkService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DatalinkService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
